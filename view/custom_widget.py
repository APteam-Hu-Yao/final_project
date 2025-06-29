from PyQt5.QtWidgets import QLabel

class custom_label(QLabel):
    def __init__(self):
        super().__init__()
        self.setObjectName("glassPanel")
        self.setStyleSheet("""
                #glassPanel {
                    background-color: rgba(250, 250, 250, 80);   /* 半透明白 */
                     border-radius: 48px;                         /* 圆角 */
                    border: 1px solid rgba(255,255,255,120);     /* 细白边 */
                }
            """)
        self.setMinimumHeight(500)