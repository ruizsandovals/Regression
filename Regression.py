from tkinter import *
from tkinter import ttk
from pandastable.core import Table
from pandastable.data import TableModel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class MyTable(Table):

    def __init__(self, parent=None, **kwargs):
        Table.__init__(self, parent, **kwargs)
        self.df = (kwargs['dataframe'])
        return


class RegressionView():

    # Constructor
    def __init__(self):
        # Parent Window
        self.root = Tk()
        self.root.geometry("1400x850")
        self.root.title("Regression exercise")

        # Frame for data table
        self.fr_data = Frame(self.root)
        self.fr_data.grid(row=0, column=0, sticky="nw", padx=25, pady=25, columnspan=2, rowspan=2)

        # Frame for variable values
        self.fr_var = Frame(self.root)
        self.fr_var.grid(row=2, column=0, sticky="nw", padx=25, columnspan=2)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)

        # Read CSV with initial data, convert all columns to float
        self.df = pd.read_csv('data.csv')
        self.dfv = pd.read_csv('mb.csv')
        self.df['AvgPrice'] = self.df['AvgPrice'].astype(float)
        self.df['Year'] = self.df['Year'].astype(float)
        self.dfv['Initial'] = self.dfv['Initial'].astype(float)
        self.dfv['End'] = self.dfv['End'].astype(float)

        # Pandas table
        # Data
        self.pt = MyTable(self.fr_data, dataframe=self.df, height=250, width=300)
        self.pt.show()
        # m and v values
        self.ptv = MyTable(self.fr_var, dataframe=self.dfv, height=200, width=300)
        self.ptv.show()

        # Scatter chart variables
        self.fig_scatter = plt.figure(figsize=(4, 3), dpi=100)
        self.ax_scatter = self.fig_scatter.add_subplot(111)
        self.canvas_scatter = FigureCanvasTkAgg(self.fig_scatter, self.root)
        self.canvas_scatter.get_tk_widget().grid(row=0, column=3, sticky='nsew', padx=25, pady=25, rowspan=4,
                                                 columnspan=2)
        self.df.plot(kind='scatter', legend=True, ax=self.ax_scatter, x='Year', y='AvgPrice', color='r', marker='o',
                     fontsize=10, grid=True)

        # SSE with respect to m
        self.fig_SSE_m = plt.figure(figsize=(4, 3), dpi=100)
        self.ax_SSE_m = self.fig_SSE_m.add_subplot(111)
        self.ax_SSE_m.set_title('SSE with respect to m')
        self.canvas_SSE_m = FigureCanvasTkAgg(self.fig_SSE_m, self.root)
        self.canvas_SSE_m.get_tk_widget().grid(row=0, column=6, sticky='nsew', padx=25, pady=25, rowspan=2)

        # SSE with respect to b
        self.fig_SSE_b = plt.figure(figsize=(4, 3), dpi=100)
        self.ax_SSE_b = self.fig_SSE_b.add_subplot(111)
        self.ax_SSE_b.set_title('SSE with respect to b')
        self.canvas_SSE_b = FigureCanvasTkAgg(self.fig_SSE_b, self.root)
        self.canvas_SSE_b.get_tk_widget().grid(row=2, column=6, sticky='nsew', padx=25, pady=25, rowspan=2)

        # Add button to refresh the chart
        self.refresh_button = Button(self.root, text="Refresh", font=("Consolas", 14))
        self.refresh_button.grid(row=4, column=6, padx=25, sticky='ne', pady=25)
        self.refresh_button.config(command=self.refresh_wdgt)

        # Labels
        self.lbl_m = Label(self.root, text='m', anchor='w', width=5)
        self.lbl_m.grid(row=3, column=0, padx=25, sticky="sw")
        self.lbl_m.config(font=("Consolas", 12))

        self.lbl_b = Label(self.root, text='b', anchor='w', width=5)
        self.lbl_b.grid(row=4, column=0, padx=25, sticky="nw")
        self.lbl_b.config(font=("Consolas", 12))

        # m scale
        self.m_value = DoubleVar()
        self.scale_m = Scale(self.root, orient=HORIZONTAL, length=200, variable=self.m_value,
                             from_=self.dfv.iloc[0]['Initial'], to=self.dfv.iloc[0]['End'],
                             resolution=0.5, showvalue=True, command=self.m_scale_event)
        self.scale_m.grid(row=3, column=1, sticky="sw")
        self.scale_m.set(1.0)

        # b scale
        self.b_value = DoubleVar()
        self.scale_b = Scale(self.root, orient=HORIZONTAL, length=200, variable=self.b_value,
                             from_=self.dfv.iloc[1]['Initial'], to=self.dfv.iloc[1]['End'],
                             resolution=0.5, showvalue=True, command=self.b_scale_event)
        self.scale_b.grid(row=4, column=1, sticky="nw")
        self.scale_b.set(0.0)

        # SSE info
        self.lblSSE = ttk.Label(self.root, text="Sum of Squared Errors", anchor="w", width=18)
        self.lblSSE.grid(row=4, column=3, padx=10, pady=25, sticky="nsew")
        self.lblSSE.config(font=("Consolas", 14))

        self.SSE = 0.0
        self.lblSSE_val = ttk.Label(self.root, width=5, text="0", anchor="w")
        self.lblSSE_val.grid(row=4, column=4, padx=10, pady=25, sticky="nsew")
        self.lblSSE_val.config(font=("Consolas", 14, "bold"), foreground="black")
        self.lblSSE_val['text'] = str(self.SSE)

        # Show charts
        self.show_charts()

        # Show the window
        self.root.mainloop()

    # Show the line based on mx + b
    def show_charts(self):
        data = []

        # Calculate all y values
        for i in range(0, len(self.df)):
            data.append(
                (self.df.iloc[i]['Year'], self.m_value.get() * i + self.b_value.get(), self.df.iloc[i]['AvgPrice']))

        # Convert list to dataframe
        df_data = pd.DataFrame(data, columns=['X', 'Y', 'AvgPrice'])
        df_data['Y-AvgPrice'] = df_data['Y'] - df_data['AvgPrice']
        df_data['SquareError'] = df_data['Y-AvgPrice'] ** 2

        # Calculate SSE
        self.SSE = df_data['SquareError'].sum()
        self.lblSSE_val['text'] = str(self.SSE)

        # Clear previous chart and ajust scale and axis
        self.ax_scatter.cla()
        self.ax_scatter.set_aspect('equal')
        min_axis = min(df_data['X'].min(), df_data['Y'].min(), df_data['AvgPrice'].min())
        max_axis = max(df_data['X'].max(), df_data['Y'].max(), df_data['AvgPrice'].max())
        self.ax_scatter.set_xlim(min_axis, max_axis)
        self.ax_scatter.set_ylim(min_axis, max_axis)

        # Show the line chart
        df_data.plot(kind='line', legend=False, ax=self.ax_scatter, x='X', y='Y', color='b', marker='o',
                     fontsize=10, grid=True)

        # Show Scatter chart
        self.df.plot(kind='scatter', legend=True, ax=self.ax_scatter, x='Year', y='AvgPrice', color='r', marker='s',
                     fontsize=10, grid=True)

        # Show squares (Standard Error)
        for i in range(0, len(df_data)):
            color = 'red' if df_data.iloc[i]['Y-AvgPrice'] < 0 else 'green'
            rect = patches.Rectangle((df_data.iloc[i]['X'], df_data.iloc[i]['AvgPrice']), df_data.iloc[i]['Y-AvgPrice'],
                                     df_data.iloc[i]['Y-AvgPrice'], facecolor=color, alpha=0.1)
            self.ax_scatter.add_patch(rect)

        # Show SSE with respect to m
        m_data = []

        # Clear canvas
        self.ax_SSE_m.cla()
        self.ax_SSE_m.set_title('SSE with respect to m (b=' + str(self.b_value.get()) + ')')

        # Get chart x axis values
        m_start = self.dfv.iloc[0]['Initial']
        m_end = self.dfv.iloc[0]['End']
        m_step = (m_end - m_start) / 10

        # Calculate y values (SSE with respect to m)
        for i in range(0, 11):
            SSE_m = 0
            for i in range(0, len(data)):
                SSE_m += ((data[i][0] * m_start + self.b_value.get()) - data[i][2]) ** 2
            m_data.append((m_start, SSE_m))
            m_start += m_step

        # Plot the chart
        df_sse_m = pd.DataFrame(m_data, columns=['X', 'Y'])
        df_sse_m.plot(kind='line', legend=False, ax=self.ax_SSE_m, x='X', y='Y', color='g', marker='o', fontsize=8,
                      grid=True)

        # Show SSE with respect to b
        b_data = []

        # Clear canvas
        self.ax_SSE_b.cla()
        self.ax_SSE_b.set_title('SSE with respect to b (m=' + str(self.m_value.get()) + ')')

        # Get chart x axis values
        b_start = self.dfv.iloc[1]['Initial']
        b_end = self.dfv.iloc[1]['End']
        b_step = (b_end - b_start) / 10

        # Calculate y values (SSE with respect to b)
        for i in range(0, 11):
            SSE_b = 0
            for i in range(0, len(data)):
                SSE_b += ((data[i][0] * self.m_value.get() + b_start ) - data[i][2]) ** 2
            b_data.append((b_start, SSE_b))
            b_start += b_step

        # Plot the chart
        df_sse_b = pd.DataFrame(b_data, columns=['X', 'Y'])
        df_sse_b.plot(kind='line', legend=False, ax=self.ax_SSE_b, x='X', y='Y', color='brown', marker='o', fontsize=8,
                      grid=True)

        # Draw all canvas again
        self.canvas_scatter.draw()
        self.canvas_SSE_m.draw()
        self.canvas_SSE_b.draw()

    # m scale event catcher
    def m_scale_event(self, event):
        self.show_charts()

    # b scale event catcher
    def b_scale_event(self, event):
        self.show_charts()

    # Refresh all widgets associated with the data
    def refresh_wdgt(self):

        # Update m and b ranges
        self.scale_m.config(to=self.dfv.iloc[0]['End'])
        self.scale_m.config(from_=self.dfv.iloc[0]['Initial'])
        self.scale_b.config(to=self.dfv.iloc[1]['End'])
        self.scale_b.config(from_=self.dfv.iloc[1]['Initial'])

        self.show_charts()


# Scatter chart variables

regression_demo = RegressionView()
