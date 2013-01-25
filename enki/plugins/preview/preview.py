"""HTML, Markdown and ReST preview
"""

import threading
import os.path

from PyQt4.QtCore import pyqtSignal, QSize, Qt, QThread, QTimer, QUrl
from PyQt4.QtGui import QIcon, QWidget

from enki.core.core import core

from enki.widgets.dockwidget import DockWidget

from enki.plugins.preview import isRestFile


class ConverterThread(QThread):
    """Thread converts markdown to HTML
    """
    htmlReady = pyqtSignal(unicode, unicode)
    
    def __init__(self):
        QThread.__init__(self)
        self._lock = threading.Lock()
    
    def process(self, filePath, language, text):
        """Convert data and emit result
        """
        with self._lock:
            self._filePath = filePath
            self._haveData = True
            self._language = language
            self._text = text
            if not self.isRunning():
                self.start(QThread.LowPriority)
    
    def _getHtml(self, language, text):
        """Get HTML for document
        """
        if language == 'HTML':
            return text
        elif language == 'Markdown':
            return self._convertMarkdown(text)
        elif language == 'ReST':
            return self._convertReST(text)
        else:
            return 'No preview for this type of file'

    def _convertMarkdown(self, text):
        """Convert Markdown to HTML
        """
        try:
            import markdown
        except ImportError:
            return 'Markdown preview requires <i>python-markdown</i> package<br/>' \
                   'Install it with your package manager or see ' \
                   '<a href="http://packages.python.org/Markdown/install.html">installation instructions</a>'

        try:
            import mdx_mathjax
        except ImportError:
            pass  #mathjax doesn't require import statement if installed as extension

        extensions = ['fenced_code', 'nl2br']
        
        # version 2.0 supports only extension names, not instances
        if markdown.version_info[0] > 2 or \
           (markdown.version_info[0] == 2 and markdown.version_info[1] > 0):
           
            class _StrikeThroughExtension(markdown.Extension):
                """http://achinghead.com/python-markdown-adding-insert-delete.html
                Class is placed here, because depends on imported markdown, and markdown import is lazy
                """
                DEL_RE = r'(~~)(.*?)~~'
                def extendMarkdown(self, md, md_globals):
                    # Create the del pattern
                    del_tag = markdown.inlinepatterns.SimpleTagPattern(self.DEL_RE, 'del')
                    # Insert del pattern into markdown parser
                    md.inlinePatterns.add('del', del_tag, '>not_strong')
            
            extensions.append(_StrikeThroughExtension())

        try:
            return markdown.markdown(text,  extensions + ['mathjax'])
        except (ImportError, ValueError):  # markdown raises ValueError or ImportError, depends on version
                                           # it is not clear, how to distinguish missing mathjax from other errors
            return markdown.markdown(text, extensions) #keep going without mathjax
    
    def _convertReST(self, text):
        """Convert ReST
        """
        try:
            import docutils.core
        except ImportError:
            return 'ReStructuredText preview requires <i>python-docutils</i> package<br/>' \
                   'Install it with your package manager or see ' \
                   '<a href="http://pypi.python.org/pypi/docutils"/>this page</a>'


        return docutils.core.publish_string(text, writer_name='html')

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            with self._lock:
                filePath = self._filePath
                language = self._language
                text = self._text
                self._haveData = False
            
            html = self._getHtml(self._language, self._text)
            
            with self._lock:
                if not self._haveData:
                    self.htmlReady.emit(filePath, html)
                    break
                # else - next iteration


class PreviewDock(DockWidget):
    """GUI and implementation
    """
    def __init__(self):
        DockWidget.__init__(self, core.mainWindow(), "&Preview", QIcon(':/enkiicons/internet.png'), "Alt+P")

        self._widget = QWidget(self)
        
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Preview.ui'), self._widget)

        self._widget.webView.page().mainFrame().titleChanged.connect(self._updateTitle)
        self.setWidget(self._widget)
        self.setFocusProxy(self._widget.webView )
        
        self._widget.cbEnableJavascript.clicked.connect(self._onJavaScriptEnabledCheckbox)
        
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)
        
        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}
        
        self._thread = ConverterThread()
        self._thread.htmlReady.connect(self._setHtml)

        self._visiblePath = None
        
        # If we update Preview on every key pressing, freezes are sensible (GUI thread draws preview too slowly
        # This timer is used for drawing Preview 300 ms After user has stopped typing text
        self._typingTimer = QTimer()
        self._typingTimer.setInterval(300)
        self._typingTimer.timeout.connect(self._scheduleDocumentProcessing)

        self._scheduleDocumentProcessing()
        self._applyJavaScriptEnabled(self._isJavaScriptEnabled())

    def del_(self):
        """Uninstall themselves
        """
        self._typingTimer.stop()
        self._thread.wait()
    
    def _updateTitle(self, pageTitle):
        """Web page title changed. Update own title
        """
        if pageTitle:
            self.setWindowTitle("&Preview - " + pageTitle)
        else:
            self.setWindowTitle("&Preview")
    
    def _saveScrollPos(self):
        """Save scroll bar position for document
        """
        frame = self._widget.webView .page().mainFrame()
        if frame.contentsSize() == QSize(0, 0):
            return # no valida data, nothing to save
        
        pos = frame.scrollPosition()
        self._scrollPos[self._visiblePath] = pos
        self._hAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Horizontal) == pos.x()
        self._vAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Vertical) == pos.y()

    def _restoreScrollPos(self):
        """Restore scroll bar position for document
        """
        try:
            self._widget.webView .page().mainFrame().contentsSizeChanged.disconnect(self._restoreScrollPos)
        except TypeError:  # already has been disconnected
            pass
        
        if not self._visiblePath in self._scrollPos:
            return  # no data for this document
        
        frame = self._widget.webView .page().mainFrame()

        frame.setScrollPosition(self._scrollPos[self._visiblePath])
        
        if self._hAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))
        
        if self._vAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if new is not None and self.isVisible():
            self._scheduleDocumentProcessing()

    def _onTextChanged(self, document):
        """Text changed, update preview
        """
        if self.isVisible():
            self._typingTimer.stop()
            self._typingTimer.start()

    def show(self):
        """When shown, update document, if posible
        """
        DockWidget.show(self)
        self._scheduleDocumentProcessing()

    def _scheduleDocumentProcessing(self):
        """Start document processing with the thread.
        """
        self._typingTimer.stop()
        
        document = core.workspace().currentDocument()
        if document is not None:
            language = document.language()
            if language is None and isRestFile(document):
                language = 'ReST'
            
            self._thread.process(document.filePath(), language, document.text())

    def _setHtml(self, filePath, html):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._widget.webView .page().mainFrame().contentsSizeChanged.connect(self._restoreScrollPos)
        self._widget.webView .setHtml(html,baseUrl=QUrl.fromLocalFile(filePath))

    def _isJavaScriptEnabled(self):
        """Check if JS is enabled in the settings
        """
        try:
            return core.config()['HtmlPreviewJavaScriptEnabled']
        except KeyError:
            return True  # default value

    def _onJavaScriptEnabledCheckbox(self, enabled):
        """Checkbox clicked, save and apply settings
        """
        core.config()['HtmlPreviewJavaScriptEnabled'] = enabled;
        core.config().flush()

        self._applyJavaScriptEnabled(enabled)

    def _applyJavaScriptEnabled(self, enabled):
        """Update QWebView settings and QCheckBox state
        """        
        self._widget.cbEnableJavascript.setChecked(enabled)
        
        settings = self._widget.webView.settings()
        settings.setAttribute(settings.JavascriptEnabled, enabled)
        
        self._scheduleDocumentProcessing()
