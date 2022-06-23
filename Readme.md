## verdigado-Layout für odoo

### Implementierungsumfang

- external_layout_standard: Kopfzeile und Fußzeile entsprechend & Schriftgröße angepasst
- sale.report_saleorder_document: Informationszeile über Angebot in Block verschoben
- account.report_invoice_document:
  * Informationszeile über Angebot in Block verschoben
  * Ausgabe der SEPA-Informationen und Überschreiben der Texte aus dem account_sepa_direct_debit Modul
- mail.mail_notification_paynow: Mail template wird überschrieben um Branding im Footer zu entfernen
- web.brand_promotion_message: Branding auf der Webseite im Footer wird entfernt


### Noch nicht implementiert

- Infoblock mit Lieferadresse und Rechnungsadresse ist aktuell entfernt (Zeilen 90/91)
