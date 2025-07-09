
from PyQt5.QtCore import QObject, pyqtSignal
from service.tcp_worker import TcpWorker, TcpThread

class MainViewModel(QObject):
    # 当收到一帧 (32,18) 的新数据时发出
    new_frame = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # 当前选中的通道索引，默认 0
        self.current_channel = 0

        # 1) 创建 TCP 后台工作者，并把它放到线程里跑
        self.worker = TcpWorker(host='localhost', port=12345)
        self.worker.frame_ready.connect(self._on_frame)

        self.thread = TcpThread(self.worker)
        self.thread.start()

    def _on_frame(self, data):
        """
        收到 TCPWorker 发来的原始数据（numpy array shape=(32,18)）
        直接把它通过 new_frame signal 向外广播
        """
        self.new_frame.emit(data)

    def select_channel(self, idx: int):
        """
        在 View 里调用：切换要显示的通道
        """
        self.current_channel = idx
