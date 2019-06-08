import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_alternative_viz as dav
import plotly_express as px
import altair as alt
from bokeh.embed import json_item
import holoviews as hv
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

hv.extension("bokeh")
gapminder = px.data.gapminder()

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

td_style = {"width": "50%", "margin": "20px"}
app.layout = html.Div([
    html.Div([ dcc.Slider(id="year", min=1952, max=2007, step=5,
                marks={x: str(x) for x in range(1952, 2008, 5)}) ],
        style={ "width": "600px", "padding-bottom": "30px", "margin": "0 auto",
                "margin-top": "-70px", "text-align": "center" } ),
    html.Table([
            html.Tr([html.Td([dcc.Graph(id="px")], style=td_style),
                     html.Td([dav.VegaLite(id="vega")], style=td_style) ]),
            html.Tr([html.Td([dav.Svg(id="seaborn")], style=td_style),
                     html.Td([dav.BokehJSON(id="bokeh")], style=td_style) ]),
        ], style={"width": "1000px", "margin": "0 auto"} ),
])

@app.callback(Output("px", "figure"), [Input("year", "value")])
def plotly_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return (px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", size_max=30,
        color="continent", log_x=True, height=400, width=600,
        title="Plotly Express", hover_name="country", hover_data=df.columns)
    .for_each_trace(lambda t: t.update(name=t.name.replace("continent=", "")))
    .update(layout_margin_t=60, layout_title_y=0.91) )

@app.callback(Output("vega", "spec"), [Input("year", "value")])
def altair_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return ( alt.Chart(df, height=250, width=400).mark_circle()
        .encode(alt.X("gdpPercap:Q", scale=alt.Scale(type="log")),
            alt.Y("lifeExp:Q", scale=alt.Scale(zero=False)),
            size="pop:Q", color="continent:N", tooltip=list(df.columns))
        .interactive().properties(title="Altair / Vega-Lite").to_dict() )

@app.callback(Output("bokeh", "json"), [Input("year", "value")])
def bokeh_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    return json_item( hv.render( hv.Points(df, kdims=["gdpPercap", "lifeExp"])
        .opts( color="continent", size=hv.dim("pop") ** (0.5) / 800,
            logx=True, height=330, width=530, cmap="Category10",tools=["hover"],
            legend_position="bottom_right", title="HoloViews / Bokeh") ))

@app.callback(Output("seaborn", "contents"), [Input("year", "value")])
def seaborn_fig(year):
    df = gapminder.query("year == %d" % (year or 1952))
    fig, ax = plt.subplots()
    sns.scatterplot( data=df, ax=ax, x="gdpPercap", y="lifeExp",
        size="pop", hue="continent", sizes=(0, 800))
    ax.set_xscale("log")
    ax.set_title("Seaborn / matplotlib")
    fig.set_size_inches(5.5, 3.7)
    fig.tight_layout()

    b_io = BytesIO()
    fig.savefig(b_io, format="svg")
    return b_io.getvalue().decode("utf-8")

if __name__ == "__main__":
    app.run_server(debug=True)
