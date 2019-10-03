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
        self.parent.Update()
        width, height = self.parent.GetSize()
        self.parent.infoBox.info.Wrap(width)

    def setProblem(self, problemName="", comment="", nodeCount=""):
        self.info.SetLabel(f"""Problem: {problemName}
Comment: {comment}
Nodes: {nodeCount}""")
        self.parent.Update()
        width, height = self.parent.GetSize()
        self.parent.infoBox.info.Wrap(width)

    def setEmpty(self):
        self.info.SetLabel("Load in a problem for details")
        self.parent.Update()


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


class loadProblem(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Problem: ")
        self.combo.Bind(wx.EVT_COMBOBOX, self._loadProblem)
        self.combo.Bind(wx.EVT_TEXT_ENTER, self._loadProblem)
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
        self.parent.infoBox.setProblem(backend.problem_name,
                                       backend.tour.comment, len(backend.tour))


class loadSolution(textDropdown):
    def __init__(self, parent, id=wx.ID_ANY):
        textDropdown.__init__(self, parent, id, "Solution: ")
        self.combo.Bind(wx.EVT_COMBOBOX, self._loadSolution)
        self.combo.Bind(wx.EVT_TEXT_ENTER, self._loadSolution)
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
        global backend, plot
        backend.draw_lines = True
        ID = int(self.combo.GetValue().split(":")[0])
        backend.fetch_solution(ID)
        plot.update()


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
        global backend, plot
        backend.solve(backend.algorithm_function,
                      backend.problem_name, backend.max_time)

        backend.draw_lines = True
        plot.update()


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
        self.infoBox = infoBox(self)
        self.infoBox.setEmpty()

        self.sizer.Add(self.title, 1, wx.CENTRE, 10)
        self.sizer.Add(self.uploadButton, 1, wx.CENTRE, 10)
        self.sizer.Add(self.loadProblem, 1, wx.CENTRE, 10)
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
        global plot
        plot = Plot(self)
        self.sizer.Add(plot, flag=wx.LEFT | wx.EXPAND)
        self.sizer.Add(sideMenu(self), 200, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Fit()
        self.Show()


# Make backend a global variable
backend = Backend()
plot = 0  # plot panel to be defined

if __name__ == "__main__":
    app = wx.App()
    gui = mainMenu()
    app.MainLoop()
