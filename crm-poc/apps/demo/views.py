from django.shortcuts import render


def organization_view(request):
    from cdms_api import api
    import json

    from django.conf import settings


    obj_result = api.get('Account', settings.CDMS_OBJ_GUID)
    # del obj_result['optevia_LastVerified']
    # del obj_result['ModifiedOn']
    # del obj_result['CreatedOn']
    # obj_result['optevia_Alias'] = 'bla ble'
    # result = api.update('Account', settings.CDMS_OBJ_GUID, json.dumps(obj_result))
    # print(result)
    import pdb; pdb.set_trace()


    return render(
        request,
        'demo/organization.html', {

        }
    )
