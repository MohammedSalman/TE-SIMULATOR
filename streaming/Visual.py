from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend
from bokeh.layouts import column, row
from bokeh.models.widgets import CheckboxGroup, Div
from bokeh.io import curdoc
from tornado import gen
import time
from bokeh.models import LabelSet
from config import TM_TYPE
from utilities import return_algorithms_names
from random import randint


class MovingAverageCalculator:

    def __init__(self):
        self.count = 0
        self._mean = 0

    def update(self, newValue):
        self.count += 1
        differential = (newValue - self._mean) / self.count
        newMean = self._mean + differential
        self._mean = newMean

    def get_mean(self):
        return '%.2f' % self._mean


class Visual:
    def __init__(self, callbackFunc, running):
        self.running = running  # Store the current state of the Flag
        self.callbackFunc = callbackFunc  # Store the callback function
        # self.all_algo = [str(a) + '+' + str(b) for a in TE_ROUTE_SELECTION_ALGORITHM for b in
        #                  TE_RATE_ADAPTATION_ALGORITHM]
        self.all_algo = return_algorithms_names()
        # if YATES_SCHEME:
        #     self.all_algo.append('YATES_SCHEME')

        self.tools = "pan,box_zoom,wheel_zoom,reset"  # Set pan, zoom, etc., options for the plot

        self.plot_options = dict(plot_height=150)  # Set plot width, height, and other plot options
        # self.plot_options = dict(plot_height=150,
        #                          tools=[self.tools])  # Set plot width, height, and other plot options

        # self.source1, self.bar1_source, self.source2, self.bar2_source = self.definePlot()  # Define various plots. Return handles for data source (self.source) and combined plot (self.pAll)
        self.time_series_sources_list, self.hbar_sources_list = self.definePlot()
        self.calc_list = []
        for algo_name in self.all_algo:
            self.calc_list.append(MovingAverageCalculator())
        # self.calc1 = MovingAverageCalculator()
        # self.calc2 = MovingAverageCalculator()

        self.doc = curdoc()  # Save curdoc() to make sure all threads see the same document. curdoc() refers to the Bokeh web document
        self.layout()  # Set the checkboxes and overall layout of the webpage
        self.prev_y1 = 0

    def definePlot(self):
        # Define plot 1 to plot raw sensor data
        # y_range = [45, 90]
        # y_range = None
        y_range = [0, 110]

        time_series_sources = []
        figures = []
        for n, algo_name in enumerate(self.all_algo):
            figures.append(
                figure(**self.plot_options, title=algo_name, y_axis_location="right", y_range=y_range))

            time_series_sources.append(
                ColumnDataSource(data=dict(time=[0], y1=[65])))
            figures[-1].line(x='time', y='y1', source=time_series_sources[-1])  # or use n instead of [-1]

        bar_sources = []
        bars_figures = []
        for algo_name in self.all_algo:
            bars_figures.append(figure(plot_height=150, plot_width=200, x_range=(0, 100)))  # y_axis_location="right",
            bar_sources.append(ColumnDataSource(dict(average=[0], algo_name=[1])))

            bars_figures[-1].hbar(y='algo_name', height=0.5, left=0, right='average', color="#CAB2D6",
                                  source=bar_sources[-1],
                                  fill_alpha=0.5)
            bars_figures[-1].yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
            # bars_figures[-1].vbar(x='algo_name', width=0.5, top='top',  color="#CAB2D6",
            #                       source=bar_sources[-1],
            #                       fill_alpha=0.5)

            # bars_figures[-1].vbar(x=[1], width=0.5, bottom=0, top=[bar_sources[-1]], source=bar_sources[-1], color="#CAB2D6")

            labels = LabelSet(y='algo_name', text='average',
                              text_font_size="18pt", level='glyph',
                              x_offset=75, y_offset=0, source=bar_sources[-1])
            bars_figures[-1].add_layout(labels)
        self.pAll = [figures, bars_figures]

        return time_series_sources, bar_sources  # Return handles to data source and gridplot

    @gen.coroutine
    def update(self, throughput_list):
        # print(throughput_list)
        for n, newy in enumerate(throughput_list):
            # rnd = randint(1, 100)
            # if n == 1 and rnd > 50:
            #     continue
            # if n == 0:
            #     time.sleep(0.5)
            t = self.time_series_sources_list[n].data['time'][-1] + 1
            # fixing the error caused by machine epsilon. Important for the visualization.
            if 99.9 < newy < 100.1:
                newy = 100
            self.calc_list[n].update(newy)
            curAvg = self.calc_list[n].get_mean()
            self.hbar_sources_list[n].patch({'average': [(0, curAvg)]})
            new_data = dict(time=[t], y1=[newy])
            self.time_series_sources_list[n].stream(new_data, rollover=300)

        # time = self.source1.data['time'][-1] + 1
        # newy1 = throughput_list[0]
        # self.calc1.update(newy1)
        # curAvg1 = self.calc1.get_mean()
        # self.bar1_source.patch({'average': [(0, curAvg1)]})
        # new_data1 = dict(time=[time], y1=[newy1])
        # self.source1.stream(new_data1, rollover=20)
        #
        # newy2 = throughput_list[1]
        # self.calc2.update(newy2)
        # curAvg2 = self.calc2.get_mean()
        # self.bar2_source.patch({'average': [(0, curAvg2)]})
        #
        # new_data2 = dict(time=[time], y1=[[newy2]])
        # self.source2.stream(new_data2, rollover=20)

    def layout(self):
        # Build presentation layout

        rows = []
        # print("here: ", len(self.pAll), len(self.pAll[0]))
        for n, algo_name in enumerate(self.all_algo):
            rows.append(row(self.pAll[0][n], self.pAll[1][n]))
        layout = column(rows)

        # row1 = row(self.pAll[0][0], self.pAll[1][0])
        # row2 = row(self.pAll[0][1], self.pAll[1][1])

        # row1 = row(self.pAll[0], self.pAll[1])
        # row2 = row(self.pAll[2], self.pAll[3])

        # layout = column(row1, row2)  # Place the text at the top, followed by checkboxes and graphs in a row below
        self.doc.title = "Real Time Routing Protocol Evaluation"  # Name of internet browser tab
        self.doc.add_root(layout)  # Add the layout to the web document
