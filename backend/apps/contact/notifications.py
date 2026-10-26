import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_new_message(contact_message):
    """Avisa por correo de un mensaje nuevo, si CONTACT_NOTIFICATION_EMAILS está configurado."""
    recipients = settings.CONTACT_NOTIFICATION_EMAILS
    if not recipients:
        return
    body = (
        f"Nombre: {contact_message.full_name}\n"
        f"Empresa: {contact_message.company or '-'}\n"
        f"E-mail: {contact_message.email}\n"
        f"Teléfono: {contact_message.phone or '-'}\n"
        f"Servicio de interés: {contact_message.service_of_interest or '-'}\n\n"
        f"{contact_message.message}"
    )
    try:
        send_mail(
            subject=f"Nuevo mensaje de contacto: {contact_message.full_name}",
            message=body,
            from_email=None,
            recipient_list=recipients,
        )
    except Exception:  # el mensaje ya quedó guardado; un fallo de correo no debe romper el formulario
        logger.exception("No se pudo enviar la notificación del mensaje de contacto %s", contact_message.pk)
