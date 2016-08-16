function return_page() {
    return '<div class="entityEditForm"><div class="formWrapper">' +
                '<div class="fieldsetWrapper" id="globalSettingId">' +
                    '<fieldset>' +
                        '<legend>Global Settings</legend>' +
                        '<div class="widget">' +
                            '<label>Logging level</label>' +
                            '<div>' +
                                '<select id="log_level_id">' +
                                    '<option selected="selected" value="INFO">INFO</option>' +
                                    '<option value="DEBUG">DEBUG</option>' +
                                    '<option value="ERROR">ERROR</option>' +
                                '</select>' +
                                '<div class="widgeterror"></div>' +
                            '</div>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="proxySettingId">' +
                    '<fieldset>' +
                        '<legend>Proxy Settings</legend>' +
                        '<div class="checkboxWidget widget">' +
                            '<div>' +
                                '<div class="widgeterror"></div>' +
                                '<div>' +
                                    '<input type="checkbox" id="enable_proxy_id" name="">' +
                                    '<span style="display:inline-block">Enable Proxy</span>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="widget" style="display: block;">' +
                            '<div class="proxy">' +
                                '<div class="widget" style="display: block;">' +
                                    '<label>Proxy host</label>' +
                                    '<div>' +
                                        '<input class="index_input" type="text" id="proxy_host_id">' +
                                    '</div>' +
                                    '<div class="widgeterror"></div>' +
                                '</div>' +
                                '<div class="widget" style="display: block;">' +
                                    '<label>Proxy port</label>' +
                                    '<div>' +
                                        '<input class="index_input" type="text" id="proxy_port_id">' +
                                    '</div>' +
                                    '<div class="widgeterror"></div>' +
                                '</div>' +
                                '<div class="widget" style="display: block;">' +
                                    '<label>Proxy username</label>' +
                                    '<div>' +
                                        '<input class="index_input" type="text" id="proxy_username_id">' +
                                    '</div>' +
                                    '<div class="widgeterror"></div>' +
                                '</div>' +
                                '<div class="widget" style="display: block;">' +
                                    '<label>Proxy password</label>' +
                                    '<div>' +
                                        '<input class="index_input" type="password" id="proxy_password_id">' +
                                    '</div>' +
                                    '<div class="widgeterror"></div>' +
                                '</div>' +
                                '<div class="widget" style="display: block;">' +
                                    '<label>Proxy type</label>' +
                                    '<div>' +
                                        '<select id="proxy_type_id">' +
                                            '<option selected="selected" value="http">http</option>' +
                                            '<option value="http_no_tunnel">http_no_tunnel</option>' +
                                            '<option value="socks4">socks4</option>' +
                                            '<option value="socks5">socks5</option>' +
                                        '</select>' +
                                        '<div class="widgeterror"></div>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="widget" style="display: block;">' +
                                    '<div>' +
                                        '<input type="checkbox" id="proxy_rdns_id" name="">' +
                                        '<span style="display:inline-block">Use Proxy to do DNS resolution</span>' +
                                    '</div>' +
                                    '<div class="widgeterror"></div>' +
                                '</div>' +
                            '</div>' +
                        '</div> <!--end of proxy div-->' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="credSettingId">' +
                    '<fieldset>' +
                        '<legend>Credential Settings</legend>' +
                        '<div>' +
                            '<span class="float-left" style="font-size:14px;">Account and Password</span>' +
                            '<a class="float-right color-gray mgr-16 credBtn" id="passwordBtnAdd">Add Account</a>' +
                        '</div>' +
                        '<br>' +
                        '<br>' +
                        '<div>' +
                            '<table id="passwordCredTable" class="table mg-10" style="display: table;">' +
                                '<thead class="tableHead">' +
                                    '<tr>' +
                                    '</tr>' +
                                '</thead>' +
                                '<tbody class="tableBody">' +
                                '</tbody>' +
                            '</table>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="apikey_SettingId">' +
                    '<fieldset>' +
                        '<legend>apikey</legend>' +
                        '<div class="widget" style="display: block;">' +
                            '<label>Cb Response API key</label>' +
                            '<div>' +
                                '<input class="index_input" type="password" id="apikey_id">' +
                            '</div>' +
                            '<div class="widgeterror" style="display: none;">' +
                            '</div>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="cburl_SettingId">' +
                    '<fieldset>' +
                        '<legend>cburl</legend>' +
                        '<div class="widget" style="display: block;">' +
                            '<label>Cb Response URL</label>' +
                            '<div>' +
                                '<input class="index_input" type="text" id="cburl_id">' +
                            '</div>' +
                            '<div class="widgeterror" style="display: none;">' +
                            '</div>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="shadow">' +
                '</div>' +
            '</div> <!-- end of form_wrapper-->' +
            '<div class="dialog passwordCredDialog">' +
                '<div id="passwordCredDialog" class="dialog-header color-gray pd-16">' +
                    'Add Account' +
                '</div>' +
                '<div class="dialog-content pd-16">' +
                    '<form autocomplete="off" id="passwordCredForm" class="credform">' +
                    '</form>' +
                '</div>' +
            '</div>' +
            '<div class="jmFormActions" style="">' +
                    '<button class="my-btn-secondary" type="button"><span>Cancel</span></button>' +
                    '<button type="submit" class="my-btn-primary"><span>Save</span></button>' +
            '</div>' +
        '</div></div>';
}

function return_cred_form() {
        return '<div class="dialog">' +
            '<div class="dialog-header pd-16">' +
                'Add New Credentials' +
            '</div>' +
            '<div class="dialog-content pd-16">' +
                '<form autocomplete="off" id="form">' +
                '</form>' +
            '</div>' +
        '</div>';
}