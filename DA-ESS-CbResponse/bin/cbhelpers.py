from cbapi import CbApi, CbEnterpriseResponseAPI


def get_creds(splunk_service):
    api_credentials = splunk_service.storage_passwords["DA-ESS-CbResponse:apikey"]
    token = api_credentials.clear_password.split("``splunk_cred_sep``")[1]

    cb_server = splunk_service.confs["DA-ESS-CbResponse_customized"]["cburl"].content['content']

    return cb_server, token


def get_legacy_cbapi(splunk_service):
    cb_server, token = get_creds(splunk_service)
    return CbApi(cb_server, ssl_verify=False, token=token)


def get_cbapi(splunk_service):
    cb_server, token = get_creds(splunk_service)
    return CbEnterpriseResponseAPI(token=token, url=cb_server, ssl_verify=False)