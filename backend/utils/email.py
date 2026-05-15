import threading
from flask import current_app
from flask_mail import Message


def _send_async(app, mail, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Error enviando email: {e}")


def _fire(mail, msg):
    app = current_app._get_current_object()
    threading.Thread(target=_send_async, args=(app, mail, msg), daemon=True).start()


# ── Plantilla base ─────────────────────────────────────────────────────────────

def _base_html(title, body_html):
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;max-width:560px;width:100%;">

      <!-- Header -->
      <tr>
        <td style="background:#111;padding:28px 40px;">
          <span style="color:#fff;font-size:1.1rem;font-weight:800;letter-spacing:2px;">URBANWEAR</span>
        </td>
      </tr>

      <!-- Título -->
      <tr>
        <td style="padding:32px 40px 0;">
          <h1 style="margin:0;font-size:1.15rem;font-weight:800;color:#111;letter-spacing:0.5px;">{title}</h1>
        </td>
      </tr>

      <!-- Cuerpo -->
      {body_html}

      <!-- Footer -->
      <tr>
        <td style="padding:24px 40px;border-top:1px solid #f0f0f0;margin-top:32px;">
          <p style="margin:0;font-size:0.75rem;color:#aaa;line-height:1.6;">
            UrbanWear &mdash; Ropa urbana hecha para ti.<br>
            Si no realizaste esta acción, puedes ignorar este correo.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


# ── Bienvenida ─────────────────────────────────────────────────────────────────

def send_welcome(mail, user):
    body = f"""
      <tr><td style="padding:20px 40px 8px;">
        <p style="margin:0;color:#555;font-size:0.9rem;line-height:1.7;">
          Hola, <strong>{user.name}</strong>. Tu cuenta fue creada exitosamente.
          Ya puedes explorar nuestro catálogo y hacer tu primer pedido.
        </p>
      </td></tr>
      <tr><td style="padding:24px 40px 32px;">
        <a href="{current_app.config.get('APP_BASE_URL', '')}/catalogo"
           style="display:inline-block;padding:13px 28px;background:#111;color:#fff;border-radius:6px;
                  text-decoration:none;font-size:0.8rem;font-weight:700;letter-spacing:1.5px;">
          IR AL CATÁLOGO
        </a>
      </td></tr>
    """
    msg = Message(
        subject='Bienvenido a UrbanWear',
        recipients=[user.email],
        html=_base_html('Tu cuenta está lista.', body)
    )
    _fire(mail, msg)


# ── Confirmación de pedido ─────────────────────────────────────────────────────

def send_order_confirmation(mail, user, order_id, items, total):
    filas_items = ''.join(
        f"""<tr>
          <td style="padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;color:#333;">
            {i['product_name']}{f' &mdash; Talla {i["size"]}' if i.get('size') else ''}
          </td>
          <td style="padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;
                     color:#888;text-align:center;">x{i['quantity']}</td>
          <td style="padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;
                     font-weight:700;color:#111;text-align:right;">
            ${i['subtotal']:,.0f}
          </td>
        </tr>"""
        for i in items
    )

    base_url = current_app.config.get('APP_BASE_URL', '')
    body = f"""
      <tr><td style="padding:16px 40px 0;">
        <p style="margin:0;color:#555;font-size:0.88rem;line-height:1.7;">
          Hola, <strong>{user.name}</strong>. Recibimos tu pedido
          <strong style="color:#111;">#{order_id}</strong> y ya está en proceso.
        </p>
      </td></tr>

      <tr><td style="padding:20px 40px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <th style="text-align:left;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">PRODUCTO</th>
            <th style="text-align:center;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">CANT.</th>
            <th style="text-align:right;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">SUBTOTAL</th>
          </tr>
          {filas_items}
          <tr>
            <td colspan="2" style="padding-top:12px;font-size:0.85rem;
                                   font-weight:700;color:#111;">TOTAL</td>
            <td style="padding-top:12px;font-size:1rem;font-weight:800;
                       color:#111;text-align:right;">${total:,.0f}</td>
          </tr>
        </table>
      </td></tr>

      <tr><td style="padding:0 40px 32px;">
        <a href="{base_url}/pedidos"
           style="display:inline-block;padding:13px 28px;background:#111;color:#fff;border-radius:6px;
                  text-decoration:none;font-size:0.8rem;font-weight:700;letter-spacing:1.5px;">
          VER MI PEDIDO
        </a>
      </td></tr>
    """
    msg = Message(
        subject=f'Orden #{order_id} recibida — UrbanWear',
        recipients=[user.email],
        html=_base_html(f'Pedido #{order_id} confirmado.', body)
    )
    _fire(mail, msg)


# ── Notificación al admin por nuevo pedido ────────────────────────────────────

def send_order_admin(mail, user, order_id, items, total):
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email:
        return

    filas_items = ''.join(
        f"""<tr>
          <td style="padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;color:#333;">
            {i['product_name']}{f' &mdash; Talla {i["size"]}' if i.get('size') else ''}
          </td>
          <td style="padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;
                     color:#888;text-align:center;">x{i['quantity']}</td>
          <td style="padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:0.85rem;
                     font-weight:700;color:#111;text-align:right;">${i['subtotal']:,.0f}</td>
        </tr>"""
        for i in items
    )

    base_url = current_app.config.get('APP_BASE_URL', '')
    body = f"""
      <tr><td style="padding:16px 40px 8px;">
        <p style="margin:0;color:#555;font-size:0.88rem;line-height:1.7;">
          <strong>{user.name}</strong> ({user.email}) acaba de realizar el pedido
          <strong style="color:#111;">#{order_id}</strong>.
        </p>
      </td></tr>
      <tr><td style="padding:12px 40px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <th style="text-align:left;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">PRODUCTO</th>
            <th style="text-align:center;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">CANT.</th>
            <th style="text-align:right;font-size:0.7rem;letter-spacing:1px;color:#aaa;
                       padding-bottom:8px;border-bottom:2px solid #111;">SUBTOTAL</th>
          </tr>
          {filas_items}
          <tr>
            <td colspan="2" style="padding-top:12px;font-size:0.85rem;font-weight:700;color:#111;">TOTAL</td>
            <td style="padding-top:12px;font-size:1rem;font-weight:800;color:#111;text-align:right;">${total:,.0f}</td>
          </tr>
        </table>
      </td></tr>
      <tr><td style="padding:12px 40px 32px;">
        <a href="{base_url}/admin/pedidos"
           style="display:inline-block;padding:13px 28px;background:#111;color:#fff;border-radius:6px;
                  text-decoration:none;font-size:0.8rem;font-weight:700;letter-spacing:1.5px;">
          VER EN EL PANEL
        </a>
      </td></tr>
    """
    msg = Message(
        subject=f'Nuevo pedido #{order_id} — {user.name}',
        recipients=[admin_email],
        html=_base_html(f'Nuevo pedido #{order_id}.', body)
    )
    _fire(mail, msg)


# ── Código de verificación de registro ────────────────────────────────────────

def send_register_code(mail, email, code):
    body = f"""
      <tr><td style="padding:16px 40px 8px;">
        <p style="margin:0;color:#555;font-size:0.88rem;line-height:1.7;">
          Ingresa este código en la pantalla de registro para crear tu cuenta.
          Válido por <strong>10 minutos</strong>.
        </p>
      </td></tr>
      <tr><td style="padding:8px 40px 32px; text-align:center;">
        <div style="display:inline-block;padding:20px 40px;background:#f5f5f5;border-radius:8px;
                    letter-spacing:14px;font-size:2rem;font-weight:800;color:#111;">{code}</div>
      </td></tr>
    """
    msg = Message(
        subject='Tu código de verificación — UrbanWear',
        recipients=[email],
        html=_base_html('Código de acceso', body)
    )
    _fire(mail, msg)


# ── Recuperar contraseña ───────────────────────────────────────────────────────

def send_password_reset(mail, user, reset_link):
    body = f"""
      <tr><td style="padding:16px 40px 8px;">
        <p style="margin:0;color:#555;font-size:0.88rem;line-height:1.7;">
          Hola, <strong>{user.name}</strong>. Recibimos una solicitud para restablecer
          la contraseña de tu cuenta. El enlace es válido por <strong>1 hora</strong>.
        </p>
      </td></tr>
      <tr><td style="padding:20px 40px 32px;">
        <a href="{reset_link}"
           style="display:inline-block;padding:13px 28px;background:#111;color:#fff;border-radius:6px;
                  text-decoration:none;font-size:0.8rem;font-weight:700;letter-spacing:1.5px;">
          RESTABLECER CONTRASEÑA
        </a>
      </td></tr>
    """
    msg = Message(
        subject='Restablece tu contraseña — UrbanWear',
        recipients=[user.email],
        html=_base_html('Solicitud de nueva contraseña.', body)
    )
    _fire(mail, msg)
