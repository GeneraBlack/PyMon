"""Settings dialog for PyMon."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pymon.core.config import Config


class SettingsDialog(QDialog):
    """Application settings dialog."""

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # ── General Tab ──
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # SSO Group
        sso_group = QGroupBox("EVE SSO Konfiguration")
        sso_layout = QFormLayout()

        self.client_id_input = QLineEdit(self.config.client_id)
        self.client_id_input.setPlaceholderText("EVE Application Client-ID eingeben...")
        sso_layout.addRow("Client-ID:", self.client_id_input)

        sso_help = QLabel(
            '<a href="https://developers.eveonline.com/applications">'
            "EVE Developer Portal</a> – Erstelle dort eine Application."
        )
        sso_help.setOpenExternalLinks(True)
        sso_layout.addRow("", sso_help)

        sso_group.setLayout(sso_layout)
        general_layout.addWidget(sso_group)

        # Application Group
        app_group = QGroupBox("Anwendung")
        app_layout = QFormLayout()

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(self.config.refresh_interval_minutes)
        self.refresh_spin.setSuffix(" Minuten")
        app_layout.addRow("Auto-Refresh Intervall:", self.refresh_spin)

        self.debug_checkbox = QCheckBox("Debug-Logging aktivieren")
        self.debug_checkbox.setChecked(self.config.debug)
        app_layout.addRow(self.debug_checkbox)

        data_dir_label = QLabel(str(self.config.data_dir))
        data_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        app_layout.addRow("Datenverzeichnis:", data_dir_label)

        db_path_label = QLabel(str(self.config.db_path))
        db_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        app_layout.addRow("Datenbank:", db_path_label)

        sde_path_label = QLabel(str(self.config.sde_db_path))
        sde_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        app_layout.addRow("SDE-Datenbank:", sde_path_label)

        app_group.setLayout(app_layout)
        general_layout.addWidget(app_group)

        # Notifications Group
        notify_group = QGroupBox("Tray-Benachrichtigungen")
        notify_layout = QFormLayout()

        self.notify_skill_complete = QCheckBox("Bei Skill-Fertigstellung benachrichtigen")
        self.notify_skill_complete.setChecked(self.config.tray_notify_skill_complete)
        notify_layout.addRow(self.notify_skill_complete)

        self.notify_queue_empty = QCheckBox("Bei leerer Skill Queue warnen")
        self.notify_queue_empty.setChecked(self.config.tray_notify_queue_empty)
        notify_layout.addRow(self.notify_queue_empty)

        self.popup_duration = QSpinBox()
        self.popup_duration.setRange(1, 30)
        self.popup_duration.setValue(self.config.tray_show_popup_duration)
        self.popup_duration.setSuffix(" Sekunden")
        notify_layout.addRow("Popup-Dauer:", self.popup_duration)

        notify_group.setLayout(notify_layout)
        general_layout.addWidget(notify_group)

        general_layout.addStretch()

        tabs.addTab(general_tab, "Allgemein")

        # ── Scopes Tab ──
        scopes_tab = QWidget()
        scopes_layout = QVBoxLayout(scopes_tab)

        scopes_label = QLabel(
            "ESI-Scopes die beim SSO-Login angefordert werden.\n"
            "Änderungen werden beim nächsten Login wirksam."
        )
        scopes_layout.addWidget(scopes_label)

        self.scopes_text = QTextEdit()
        self.scopes_text.setPlainText("\n".join(self.config.scopes))
        self.scopes_text.setFont(self.font())
        scopes_layout.addWidget(self.scopes_text)

        tabs.addTab(scopes_tab, "Scopes")

        # ── Email Tab ──
        email_tab = QWidget()
        email_layout = QVBoxLayout(email_tab)

        email_group = QGroupBox("E-Mail-Benachrichtigungen")
        email_form = QFormLayout()

        self.email_enabled = QCheckBox("E-Mail-Benachrichtigungen aktivieren")
        self.email_enabled.setChecked(self.config.email_enabled)
        email_form.addRow(self.email_enabled)

        self.email_smtp_server = QLineEdit(self.config.email_smtp_server)
        self.email_smtp_server.setPlaceholderText("z.B. smtp.gmail.com")
        email_form.addRow("SMTP Server:", self.email_smtp_server)

        self.email_smtp_port = QSpinBox()
        self.email_smtp_port.setRange(1, 65535)
        self.email_smtp_port.setValue(self.config.email_smtp_port)
        email_form.addRow("SMTP Port:", self.email_smtp_port)

        self.email_smtp_user = QLineEdit(self.config.email_smtp_user)
        self.email_smtp_user.setPlaceholderText("user@example.com")
        email_form.addRow("Benutzername:", self.email_smtp_user)

        self.email_smtp_password = QLineEdit(self.config.email_smtp_password)
        self.email_smtp_password.setEchoMode(QLineEdit.EchoMode.Password)
        email_form.addRow("Passwort:", self.email_smtp_password)

        self.email_to_input = QLineEdit(self.config.email_to)
        self.email_to_input.setPlaceholderText("empfaenger@example.com")
        email_form.addRow("Empfänger:", self.email_to_input)

        self.email_use_tls = QCheckBox("TLS verwenden (empfohlen)")
        self.email_use_tls.setChecked(self.config.email_use_tls)
        email_form.addRow(self.email_use_tls)

        test_email_btn = QPushButton("📧 Test-E-Mail senden")
        test_email_btn.clicked.connect(self._send_test_email)
        email_form.addRow(test_email_btn)

        email_group.setLayout(email_form)
        email_layout.addWidget(email_group)
        email_layout.addStretch()

        tabs.addTab(email_tab, "E-Mail")

        # ── Cloud Sync Tab ──
        cloud_tab = QWidget()
        cloud_layout = QVBoxLayout(cloud_tab)

        cloud_group = QGroupBox("Cloud Storage Sync")
        cloud_form = QFormLayout()

        cloud_info = QLabel(
            "Synchronisiere Daten mit einem lokalen Cloud-Ordner\n"
            "(Dropbox, Google Drive, OneDrive etc.)."
        )
        cloud_info.setWordWrap(True)
        cloud_form.addRow(cloud_info)

        sync_row = QHBoxLayout()
        self.cloud_sync_path = QLineEdit(self.config.cloud_sync_path)
        self.cloud_sync_path.setPlaceholderText("z.B. C:\\Users\\…\\Dropbox")
        sync_row.addWidget(self.cloud_sync_path)
        browse_btn = QPushButton("📂 Durchsuchen…")
        browse_btn.clicked.connect(self._browse_cloud_folder)
        sync_row.addWidget(browse_btn)
        cloud_form.addRow("Sync-Ordner:", sync_row)

        cloud_group.setLayout(cloud_form)
        cloud_layout.addWidget(cloud_group)
        cloud_layout.addStretch()

        tabs.addTab(cloud_tab, "Cloud Sync")

        # ── Auto-Update Tab ──
        update_tab = QWidget()
        update_layout = QVBoxLayout(update_tab)

        update_group = QGroupBox("Auto-Update")
        update_form = QFormLayout()

        self.auto_update_check = QCheckBox("Beim Start auf Updates prüfen")
        self.auto_update_check.setChecked(self.config.auto_update_check)
        update_form.addRow(self.auto_update_check)

        update_info = QLabel(
            "PyMon prüft beim Start, ob eine neue Version auf GitHub verfügbar ist.\n"
            "Es werden keine Daten automatisch heruntergeladen."
        )
        update_info.setWordWrap(True)
        update_form.addRow(update_info)

        update_group.setLayout(update_form)
        update_layout.addWidget(update_group)
        update_layout.addStretch()

        tabs.addTab(update_tab, "Updates")

        layout.addWidget(tabs)

        # ── Buttons ──
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        """Save settings and close."""
        self.config.client_id = self.client_id_input.text().strip()
        self.config.debug = self.debug_checkbox.isChecked()
        self.config.refresh_interval_minutes = self.refresh_spin.value()
        self.config.tray_notify_skill_complete = self.notify_skill_complete.isChecked()
        self.config.tray_notify_queue_empty = self.notify_queue_empty.isChecked()
        self.config.tray_show_popup_duration = self.popup_duration.value()

        # Parse scopes
        scopes_text = self.scopes_text.toPlainText().strip()
        if scopes_text:
            self.config.scopes = [
                s.strip() for s in scopes_text.split("\n") if s.strip()
            ]

        # Email settings
        self.config.email_enabled = self.email_enabled.isChecked()
        self.config.email_smtp_server = self.email_smtp_server.text().strip()
        self.config.email_smtp_port = self.email_smtp_port.value()
        self.config.email_smtp_user = self.email_smtp_user.text().strip()
        self.config.email_smtp_password = self.email_smtp_password.text()
        self.config.email_to = self.email_to_input.text().strip()
        self.config.email_use_tls = self.email_use_tls.isChecked()

        # Cloud Sync
        self.config.cloud_sync_path = self.cloud_sync_path.text().strip()

        # Auto-Update
        self.config.auto_update_check = self.auto_update_check.isChecked()

        self.accept()

    def _send_test_email(self) -> None:
        """Send a test email with current settings."""
        from pymon.services.email_notifier import EmailNotifier

        notifier = EmailNotifier(
            smtp_server=self.email_smtp_server.text().strip(),
            smtp_port=self.email_smtp_port.value(),
            smtp_user=self.email_smtp_user.text().strip(),
            smtp_password=self.email_smtp_password.text(),
            email_to=self.email_to_input.text().strip(),
            use_tls=self.email_use_tls.isChecked(),
        )
        if not notifier.is_configured:
            QMessageBox.warning(self, "E-Mail", "Bitte alle SMTP-Felder ausfüllen.")
            return

        ok = notifier.send_test()
        if ok:
            QMessageBox.information(self, "E-Mail", "✓ Test-E-Mail erfolgreich gesendet!")
        else:
            QMessageBox.critical(self, "E-Mail", "✗ Senden fehlgeschlagen. Prüfe die Einstellungen.")

    def _browse_cloud_folder(self) -> None:
        """Browse for a cloud sync folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Cloud Sync-Ordner wählen", self.cloud_sync_path.text()
        )
        if folder:
            self.cloud_sync_path.setText(folder)
