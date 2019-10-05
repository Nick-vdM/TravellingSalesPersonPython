import wx
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

import TSP_db
import TSP


class Backend(TSP_db.Database):
    def __init__(self):
        TSP_db.Database.__init__(self)
        self.algorithm_function = TSP.greedy  # to save the algorithm
        self.max_time = 10
        self.draw_lines = False

        self.problems_rows = []
        self._load_all_problems()

        self.solution_rows = []
        solution_lengths = []

    def _load_all_problems(self):
        query = """
        SELECT *
        FROM Problem"""
        self.cursor.execute(query)
        self.problems_rows = self.cursor.fetchall()

    def fetch_solutions_to(self, problem_name):
        query = """
        SELECT *
        FROM Solution
        WHERE ProblemName = '{problem_name}'"""
        self.cursor.execute(query)
        self.solution_rows = self.cursor.fetchall()
        for r in self.cursor.fetchall():
            self.problem_names.append(r[2])


class Plot(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id=id)
        self.parent = parent
        self.figure = mpl.figure.Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        global axes
        self.axes = self.figure.add_subplot(111)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, proportion=1, flag=wx.EXPAND | wx.ALL)
        self.sizer.Add(self.toolbar, proportion=0, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)
        self.Show()
        self.lastWidth, self.lastHeight = self.parent.GetSize()

    def update(self):
        """Plots whatever's on backed"""
        global backend
        self.axes.clear()
        # Load in coords
        x = []
        y = []
        for i in backend.tour.route:
            x.append(i.x)
            y.append(i.y)
        x.append(backend.tour.route[0].x)
        y.append(backend.tour.route[0].y)
        if backend.draw_lines:
            self.axes.plot(x, y)
        else:
            self.axes.scatter(x, y)
        self.canvas.draw()


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
        self.parent = parent
        self.info = wx.StaticText(self, label="")
        font = self.info.GetFont()
        font.PointSize = 15
        self.info.SetFont(font)
        self.box = wx.BoxSizer()
        self.box.Add(self.info, 1, wx.ALIGN_TOP | wx.EXPAND, border=10)
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
        self.parent.Refresh()
        width, height = self.parent.GetSize()
        global info
        info.info.Wrap(width)

    def setProblem(self, problemName="", comment="", nodeCount=""):
        self.info.SetLabel(f"""Problem: {problemName}
Comment: {comment}
Nodes: {nodeCount}""")
        self.parent.Refresh()
        width, height = self.parent.GetSize()
        global info
        info.info.Wrap(width)

    def setEmpty(self):
        self.info.SetLabel("Load in a problem for details")
        self.parent.Refresh()


class uploadButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.id = id

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.problemButton = wx.Button(self,
                                       label="Upload")
        self.sizer.Add(self.problemButton, wx.ALIGN_LEFT)
        self.problemButton.Bind(wx.EVT_BUTTON, self._onButton)

    def _onButton(self, event):
        """Bring up the load file interface"""
        print("Launched problem select dialogue")
        frame = wx.Frame(None, wx.ID_ANY, "Upload")
        filepath = self._getFile(frame)
        problemName = self._getName(frame)
        backend.add_problem(problemName, filepath)
        frame.Destroy()
        # Reload problem list
        self.parent.loadProblem.setList()

    def _getFile(self, frame):
        """Opens a prompt to pick a file"""
        # TODO: on event close situations; otherwise _onButton will
        # keep running
        openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                       "TSP files (*.tsp)|*.tsp",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        path = openFileDialog.GetPath()
        global backend
        openFileDialog.Destroy()
        return path

    def _getName(self, frame):
        fileNameDlg = wx.TextEntryDialog(frame, "Pick a file name",
                                         "Name picker")
        if wx.ID_OK == fileNameDlg.ShowModal():
            string = fileNameDlg.GetValue()
            fileNameDlg.Destroy()
            return string


class textDropdown(wx.Panel):
    """Combines a static text and dropdown"""

    def __init__(self, parent, id=wx.ID_ANY, text=""):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.id = id
        self.info = wx.StaticText(self, label=text)
        height, width = parent.GetSize()
        self.combo = wx.ComboBox(self, size=(width * 10, height * 1.1))
        height, width = self.combo.GetSize()
        self.infoButton = wx.Button(self, wx.ID_ANY, size=(width, width))
        self.infoButton.SetBitmapLabel(
            wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, size=(width * 0.8, width * 0.8)))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.info, flag=wx.ALIGN_CENTRE_HORIZONTAL, border=10)
        self.sizer.Add(self.combo, flag=wx.ALIGN_CENTRE_HORIZONTAL, border=5)
        self.sizer.Add(self.infoButton)
        self.infoButton.Bind(wx.EVT_BUTTON, self.showInfo)
        self.SetSizer(self.sizer)

    def showInfo(self):
        """Launches a wxControl to show information"""
        pass


class queryWindow(wx.Frame):
    """Runs a query and displays all the information"""

    def __init__(self, title, query, parent=None, id=wx.ID_ANY):
        wx.Frame.__init__(self, None, id, title)

        self.panel = wx.Panel(self, wx.ID_ANY)
        global plot, backend
        self.listCtrl = wx.ListCtrl(self.panel,
                                    size=plot.GetSize(),
                                    style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.listCtrl, wx.EXPAND)
        self.panel.SetSizer(self.sizer)

        self.setTitles(query)
        self.addData()

        self.Bind(wx.EVT_CLOSE, self._closeWindow)
        self.Show()

    def setTitles(self, query):
        global backend
        backend.cursor.execute(query)
        self.fieldCount = len(backend.cursor.description)
        self.fieldNames = [title[0] for title in backend.cursor.description]
        for i in range(self.fieldCount):
            self.listCtrl.InsertColumn(i, self.fieldNames[i])

    def addData(self):
        global backend
        index = 0
        for r in backend.cursor.fetchall():
            self.listCtrl.InsertItem(index, "")
            for i in range(self.fieldCount):
                self.listCtrl.SetItem(index, i, str(r[i]).strip())
            index += 1

    def _closeWindow(self, event):
        # Event handlers pass an extra argument so define it like this
        self.Destroy()


class loadProblem(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Problem: ")
        self.combo.Bind(wx.EVT_COMBOBOX, self._loadProblem)
        self.combo.Bind(wx.EVT_TEXT_ENTER, self._loadProblem)
        self.infoButton.Bind(wx.EVT_BUTTON, self._onInfo)
        self.setList()

    def setList(self):
        global backend
        self.combo.Clear()
        for n in backend.problems_rows:
            self.combo.Append(n[0])

    def _loadProblem(self, event):
        global backend, plot
        backend.draw_lines = False
        backend.load_in_problem(self.combo.GetValue())
        plot.update()
        self.parent.loadSolution.setList(self.combo.GetValue())
        backend.problem_name = self.combo.GetValue()
        global info
        info.setProblem(backend.problem_name,
                        backend.tour.comment, len(backend.tour))

    def _onInfo(self, event):
        queryWindow("Problems list", """
        SELECT *
        FROM Problem""")


class loadSolution(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Solution: ")
        self.combo.Bind(wx.EVT_COMBOBOX, self._loadSolution)
        self.combo.Bind(wx.EVT_TEXT_ENTER, self._loadSolution)
        self.infoButton.Bind(wx.EVT_BUTTON, self._onInfo)
        self.combo.Enable(False)
        self.combo.SetValue(text="Select a problem first")

    def setList(self, problem_name):
        """Sets the avaiable solutions"""
        global backend
        self.combo.Enable(True)
        self.combo.Clear()
        backend.cursor.execute(f"""
            SELECT SolutionID, TourLength
            FROM Solution
            WHERE  ProblemName = "{problem_name}"
            ORDER BY TourLength
        """)
        for r in backend.cursor.fetchall():
            string = str(r[0]) + ": Length: " + str(round(r[1], 3))
            self.combo.Append(string)

    def _loadSolution(self, event):
        global backend, plot, info
        backend.draw_lines = True
        ID = int(self.combo.GetValue().split(":")[0])
        backend.fetch_solution(ID)
        plot.update()
        info.setSolution(problemName=backend.problem_name,
                         comment=backend.tour.comment,
                         nodeCount=len(backend.tour),
                         solutionId=ID,
                         length=round(backend.tour.get_dist(), 3),
                         runtime=round(backend.run_time, 3),
                         algo=backend.algorithm_function.__name__,
                         author=backend.author,
                         date=backend.date)

    def _onInfo(self, event):
        global backend
        if backend.problem_name:
            queryWindow("Solutions list", f"""
            SELECT *
            FROM Solution
            WHERE ProblemName = {backend.problem_name}""")
        else:
            queryWindow("Solutions list", """
            SELECT *
            FROM Solution""")


class solveButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.sizer = wx.BoxSizer()

        self.solveButton = wx.Button(self, label="Solve")
        height, width = self.solveButton.GetSize()

        gear_icon = wx.Image("gear.png", wx.BITMAP_TYPE_ANY).Scale(width, width)
        gear_icon = wx.BitmapFromImage(gear_icon)
        self.settingsButton = wx.BitmapButton(self, bitmap=gear_icon, size=(width, width), style=wx.BU_EXACTFIT)

        self.sizer.Add(self.solveButton)
        self.sizer.Add(self.settingsButton, flag=wx.RIGHT | wx.BOTTOM, border=10)

        self.Bind(wx.EVT_BUTTON, self._onSolve, self.solveButton)
        self.Bind(wx.EVT_BUTTON, self._onSettings, self.settingsButton)

        self.SetSizer(self.sizer)
        self.Fit()

    def _onSolve(self, event):
        global backend, plot, info
        backend.solve(backend.algorithm_function,
                      backend.problem_name, backend.max_time)
        backend.draw_lines = True
        plot.update()
        info.setSolution(problemName=backend.problem_name,
                         comment=backend.tour.comment,
                         nodeCount=len(backend.tour),
                         solutionId='Save for id',
                         length=round(backend.tour.get_dist(), 3),
                         runtime=round(backend.run_time, 3),
                         algo=backend.algorithm_function.__name__,
                         author=backend.author,
                         date=backend.date)

    def _onSettings(self, event):
        pass


class saveButton(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.id = id
        self.sizer = wx.BoxSizer()

        self.saveButton = wx.Button(self, label="Save Solution")
        height, width = self.saveButton.GetSize()

        gear_icon = wx.Image("gear.png", wx.BITMAP_TYPE_ANY).Scale(width, width)
        gear_icon = wx.BitmapFromImage(gear_icon)
        self.settingsButton = wx.BitmapButton(self, bitmap=gear_icon, size=(width, width), style=wx.BU_EXACTFIT)

        self.sizer.Add(self.saveButton)
        self.sizer.Add(self.settingsButton, flag=wx.RIGHT | wx.BOTTOM, border=10)

        self.Bind(wx.EVT_BUTTON, self._onSave, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self._onSettings, self.settingsButton)

        self.SetSizer(self.sizer)
        self.Fit()

    def _onSave(self, event):
        global backend
        backend.save_tour_as_solution()
        self.parent.loadSolution.setList(backend.problem_name)

    def _onSettings(self, event):
        pass


class sideMenu(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.id = id
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = title(self)
        self.uploadButton = uploadButton(self)
        self.loadProblem = loadProblem(self)
        self.loadSolution = loadSolution(self)
        self.solveButton = solveButton(self)
        self.saveButton = saveButton(self)
        self.line = wx.StaticLine(self, -1, style=wx.HORIZONTAL)

        self.sizer.Add(self.title, 1, wx.CENTRE, 10)
        self.sizer.Add(self.uploadButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.loadProblem, 1, wx.CENTRE, 10)
        self.sizer.Add(self.loadSolution, 1, wx.CENTRE, 10)
        self.sizer.Add(self.solveButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.saveButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.line, 0, wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer)


class mainMenu(wx.Frame):
    def __init__(self, parent=None, id=wx.ID_ANY, title="Travelling Salesperson Visualiser"):
        wx.Frame.__init__(self, parent, id, title)
        self.SetMinSize((800, 600))
        self.parent = parent
        self.id = id

        self.mainSplitter = wx.SplitterWindow(self, style=wx.SP_BORDER)
        self.rightSplitter = wx.SplitterWindow(self.mainSplitter, style=wx.SP_BORDER)

        self.menu = sideMenu(self.rightSplitter)
        global info
        info = infoBox(self.rightSplitter)
        info.setEmpty()

        self.rightSplitter.SplitHorizontally(self.menu, info)
        self.rightSplitter.SetMinimumPaneSize(150)
        self.rightSplitter.SetSashPosition(300)
        self.rightSplitter.SetSashGravity(0.6)

        global plot
        plot = Plot(self.mainSplitter)

        self.mainSplitter.SplitVertically(plot, self.rightSplitter)
        self.mainSplitter.SetMinimumPaneSize(300)
        self.mainSplitter.SetSashPosition(800 * 0.7)
        self.mainSplitter.SetSashGravity(0.7)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mainSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Fit()
        self.Show()


# Make backend a global variable
backend = Backend()
plot = 0  # plot panel to be defined
info = 0  # information panel

if __name__ == "__main__":
    app = wx.App()
    gui = mainMenu()
    app.MainLoop()
