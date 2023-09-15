from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import logging
from pytube import Playlist
import re
import requests
import base64
from werkzeug import urls

_logger = logging.getLogger(__name__)

class InvoiceMenu(models.Model):
    _name = "content.playlist"
    _description = "Content Playlist"

    playlist_url = fields.Char(string='Playlist URL', required=True)

    

    def _find_document_data_from_url(self, url):
        url_obj = urls.url_parse(url)

        if url_obj.ascii_host == 'youtu.be':
            return ('youtube', url_obj.path[1:] if url_obj.path else False)
        elif url_obj.ascii_host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'www.youtube-nocookie.com'):
            v_query_value = url_obj.decode_query().get('v')
    
            if v_query_value:
                return ('youtube', v_query_value)
            split_path = url_obj.path.split('/')
    
            if len(split_path) >= 3 and split_path[1] in ('v', 'embed'):
                return ('youtube', split_path[2])

        expr = re.compile(r'(^https:\/\/docs.google.com|^https:\/\/drive.google.com).*\/d\/([^\/]*)')
        arg = expr.match(url)
        document_id = arg and arg.group(2) or False
        if document_id:
            return ('google', document_id)

        return (None, False)    

    def _parse_document_url(self, url, only_preview_fields=False):
        document_source, document_id = self._find_document_data_from_url(url)
        if document_source:
            return getattr(self,'_parse_%s_document' % document_source)(document_id, only_preview_fields)
        return {'error': _('Unknown document')}    

    def _fetch_data(self, base_url, params, content_type=False):
        result = {'values': dict()}
        try:
            response = requests.get(base_url, timeout=3, params=params)
            response.raise_for_status()
            if content_type == 'json':
                result['values'] = response.json()
            elif content_type in ('image', 'pdf'):
                result['values'] = base64.b64encode(response.content)
            else:
                result['values'] = response.content
        except requests.exceptions.HTTPError as e:
            result['error'] = e.response.content
        except requests.exceptions.ConnectionError as e:
            result['error'] = str(e)
        return result
    
    def _parse_youtube_document(self, document_id, only_preview_fields):
        """ If we receive a duration (YT video), we use it to determine the slide duration.
        The received duration is under a special format (e.g: PT1M21S15, meaning 1h 21m 15s). """

        key = self.env['website'].get_current_website().website_slide_google_app_key
        fetch_res = self._fetch_data('https://www.googleapis.com/youtube/v3/videos', {'id': document_id, 'key': key, 'part': 'snippet,contentDetails', 'fields': 'items(id,snippet,contentDetails)'}, 'json')
        if fetch_res.get('error'):
            return {'error': self._extract_google_error_message(fetch_res.get('error'))}

        values = {'slide_type': 'video', 'document_id': document_id}
        items = fetch_res['values'].get('items')
        if not items:
            return {'error': _('Please enter valid Youtube or Google Doc URL')}
        youtube_values = items[0]

        youtube_duration = youtube_values.get('contentDetails', {}).get('duration')
        if youtube_duration:
            parsed_duration = re.search(r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', youtube_duration)
            if parsed_duration:
                values['completion_time'] = (int(parsed_duration.group(1) or 0)) + \
                                            (int(parsed_duration.group(2) or 0) / 60) + \
                                            (int(parsed_duration.group(3) or 0) / 3600)

        if youtube_values.get('snippet'):
            snippet = youtube_values['snippet']
            if only_preview_fields:
                values.update({
                    'url_src': snippet['thumbnails']['high']['url'],
                    'title': snippet['title'],
                    'description': snippet['description']
                })

                return values

            values.update({
                'name': snippet['title'],
                'image_1920': self._fetch_data(snippet['thumbnails']['high']['url'], {}, 'image')['values'],
                'description': snippet['description'],
                'mime_type': False,
            })
        return {'values': values}

    def get_url_list(self,playlist):
        urls = []
        try:
            playlist_urls = Playlist(playlist)
        except Exception as e:
            # raise ValidationError(_("For single video, Please Try with 'Add Content' Button.\n'OR'\nPlease ! Provide Playlist"))
            raise ValidationError(_("Please ! Provide Playlist"))
        for url in playlist_urls:
             urls.append(url)

        return urls 
    
    def add_content_playlist_video(self):
        context = self.env.context

        playlist_urls = self.get_url_list(self.playlist_url)
        count = 0 
        for url in playlist_urls:
            res = self._parse_document_url(url)
            if res.get('error'):
                raise UserError(res.get('error')) 
            values = res['values']
            if not values.get('document_id'):
                raise UserError(_('Please enter valid Youtube or Google Doc URL'))
            values['channel_id'] = context['active_id']
            values['url'] = url
            content_id = self.env['slide.slide'].create(values)
            print("content_id == ",content_id)

        print("success")


        

