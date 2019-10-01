import wx
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit
from numpy import arange, sin, pi
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar


class Plot(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id=id)
        self.parent = parent
        self.figure = mpl.figure.Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.axes = self.figure.add_subplot(111)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas)
        self.sizer.Add(self.toolbar)
        self.SetSizer(self.sizer)
        self.Show()
        self.lastWidth, self.lastHeight = self.parent.GetSize()


class title(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent)
        self.info = wx.StaticText(self, label="TSP Solver 3000")
        font = self.info.GetFont()
        font.Family = wx.MODERN
        font.PointSize = 20
        font = font.Bold()
        self.info.SetFont(font)
        self.box = wx.BoxSizer()
        self.box.Add(self.info, wx.ALIGN_TOP | wx.EXPAND, border=10)


class infoBox(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.info = wx.StaticText(self, label="")
        font = self.info.GetFont()
        font.PointSize = 15
        self.info.SetFont(font)
        self.box = wx.BoxSizer()
        self.box.Add(self.info, wx.ALIGN_TOP | wx.EXPAND, border=10)
        self.setEmpty()

    def setSolution(self, problemName="", comment="", nodeCount="",
                    solutionId="", length="",
                    runtime="", algo="", author="", date=""):
        self.info.SetLabel(f"""Problem: {problemName}
Comment: {comment}
Nodes: {nodeCount}
Solution ID: {solutionId}
Length: {length}
Runtime: {runtime}
Algorithm: {algo}
Author: {author}
Date: {date}""")

    def setProblem(self, problemName="", comment="", nodeCount=""):
        self.info.SetLabel(f"""Problem: {problemName}
Comment: {comment}
Nodes: {nodeCount}
\n
\n
\n
\n
\n
\n""")

    def setEmpty(self):
        self.info.SetLabel("Load in a problem for details\n\n\n\n\n\n")


class uploadButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.problemButton = wx.Button(self,
                                       label="Upload")
        self.sizer.Add(self.problemButton, wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self._onButton(), self)

    def _onButton(self):
        """Bring up the load file interface"""
        pass


class textDropdown(wx.Panel):
    """Combines a static text and dropdown"""

    def __init__(self, parent, id=wx.ID_ANY, text=""):
        wx.Panel.__init__(self, parent, id)
        self.info = wx.StaticText(self, label=text)
        self.combo = wx.ComboBox(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.info, flag=wx.TOP | wx.LEFT, border=10)
        self.sizer.Add(self.combo, flag=wx.TOP, border=5)
        self.SetSizer(self.sizer)

    def setComboInfo(self, data):
        pass


class loadProblem(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Problem: ")

    def _loadProblem(self):
        pass

    def _loadSolution(self):
        pass


class loadSolution(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Solution: ")

    def _loadProblem(self):
        pass

    def _loadSolution(self):
        pass


class solveButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.solveButton = wx.Button(self,
                                     label="Solve")
        self.settingsButton = wx.Button(self,
                                        label="GearIcon")
        self.sizer.Add(self.solveButton, flag=wx.EXPAND, border=10)
        self.sizer.Add(self.settingsButton, flag=wx.ALIGN_CENTRE_HORIZONTAL, border=5)

        self.Bind(wx.EVT_BUTTON, self._onSolve,
                  self.solveButton)
        self.Bind(wx.EVT_BUTTON, self._onSettings(),
                  self.settingsButton)

    def _onSolve(self):
        pass

    def _onSettings(self):
        pass


class saveButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.solveButton = wx.Button(self,
                                     label="Save Solution")
        self.settingsButton = wx.Button(self,
                                        label="Settings icon")
        self.sizer.Add(self.solveButton, wx.ALIGN_LEFT)
        self.sizer.Add(self.settingsButton, wx.ALIGN_RIGHT)

        self.Bind(wx.EVT_BUTTON, self._onSolve,
                  self.solveButton)
        self.Bind(wx.EVT_BUTTON, self._onSettings(),
                  self.settingsButton)

    def _onSolve(self):
        pass

    def _onSettings(self):
        pass

    def onButton(self):
        pass


class sideMenu(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.id = id
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = title(self)
        self.uploadButton = uploadButton(self)
        self.loadButtons = loadProblem(self)
        self.loadSolution = loadSolution(self)
        self.solveButton = solveButton(self)
        self.saveButton = saveButton(self)
        self.line = wx.StaticLine(self, -1, style=wx.HORIZONTAL)
        self.infoBox = infoBox(self)
        self.infoBox.setSolution()

        self.sizer.Add(self.title, 1, wx.CENTRE, 10)
        self.sizer.Add(self.uploadButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.loadButtons, 1, wx.CENTRE, 10)
        self.sizer.Add(self.loadSolution, 1, wx.CENTRE, 10)
        self.sizer.Add(self.solveButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.saveButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.line, 0, wx.ALL | wx.EXPAND)
        self.sizer.Add(self.infoBox, 0, wx.LEFT, 10)
        self.SetSizer(self.sizer)


class mainMenu(wx.Frame):
    def __init__(self, parent=None, id=wx.ID_ANY, title="Travelling Salesperson Visualiser"):
        wx.Frame.__init__(self, parent, id, title)
        self.SetMinSize((1000, 600))
        self.parent = parent
        self.id = id

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(Plot(self), flag=wx.LEFT | wx.EXPAND)
        self.sizer.Add(sideMenu(self), 200, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Fit()
        self.Show()


if __name__ == "__main__":
    app = wx.App()
    gui = mainMenu()
    app.MainLoop()
