from bills.models import Service


def handle_service_instance(service_name):
    service_instance = {}
    service_name = service_name.title()

    try:
        service_instance = Service.objects.get(name=service_name)
    except Service.DoesNotExist:
        service_instance = Service.objects.create(name=service_name)

    return service_instance
    