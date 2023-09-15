/** @odoo-module **/

import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";
import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";



patch(SwitchCompanyMenu.prototype, "web.SwitchCompanyMenu",{

    toggleCompany(companyId) {
        this.state.companiesToToggle = symmetricalDifference(this.state.companiesToToggle, [
            companyId,
        ]);
        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            this.companyService.setCompanies("toggle", ...this.state.companiesToToggle);
        }, this.constructor.toggleDelay);
    },

    logIntoCompany(companyId) {
        browser.clearTimeout(this.toggleTimer);
        this.companyService.setCompanies("loginto", companyId);
    },

    get isSelectedAll() {
        const idsList = Object.keys(this.companyService.availableCompanies).filter(cId => cId > 0).map(Number);
        const isAll = symmetricalDifference(idsList, this.selectedCompanies);
        return (isAll && isAll.length === 0) ? true : false;;
    }

});

