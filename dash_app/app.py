import typing as t
import dash_mantine_components as dmc

from datetime import datetime
from dash import (
    clientside_callback,
    Dash,
    html,
    dcc,
    callback,
    Output,
    Input,
    State,
    no_update,
    ctx,
)
from dash_iconify import DashIconify
from dash_app.quotes import get_question_pairs


QUOTES_PER_DAY = 10
HIDE = {"display": "none"}
DISPLAY = {"display": "block"}
CARD_STYLE = {"minHeight": "32vh"}


app = Dash(__name__)
server = app.server


initial_content = dmc.Stack(
    [
        dmc.Container(
            dmc.Paper(
                """
                You will be presented with two quotes. One of the quotes
                is from a real person, and the other one is generated by
                ChatGPT. Your task is to guess which one is AI!
                """,
                radius="xl",
                p="xl",
                shadow="md",
                withBorder=True,
            )
        ),
        dmc.Button(
            "Let's go!",
            id="acknowledge-button",
            size="md",
            radius="xl",
            color="dark",
            rightIcon=DashIconify(icon="icon-park-solid:next"),
        ),
    ],
    align="center",
    mx=20,
    id="initial-content",
)


content = dmc.Stack(
    [
        dmc.Container(
            [
                dmc.Card(
                    children=[
                        dmc.Container(
                            dmc.Blockquote(id="quote-0"),
                        ),
                        dmc.Center(
                            dmc.Chip(
                                DashIconify(icon="twemoji:robot"),
                                id="select-0",
                                size="xl",
                            ),
                        ),
                    ],
                    id="card-0",
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    style=CARD_STYLE,
                ),
                dmc.Space(h=10),
                dmc.Card(
                    children=[
                        dmc.Container(
                            dmc.Blockquote(id="quote-1"),
                        ),
                        dmc.Center(
                            dmc.Chip(
                                DashIconify(icon="twemoji:robot"),
                                id="select-1",
                                size="xl",
                            ),
                        ),
                    ],
                    id="card-1",
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    style=CARD_STYLE,
                ),
            ]
        ),
        dmc.Space(h=10),
        dmc.Container(
            dmc.Stack(
                [
                    dmc.Button(
                        "Submit",
                        disabled=True,
                        id="submit-button",
                        size="xl",
                        radius="xl",
                        rightIcon=DashIconify(icon="formkit:submit"),
                    ),
                    dmc.Progress(
                        id="progress-bar",
                        value=0,
                        size="xl",
                        radius="xl",
                        animate=True,
                    ),
                ]
            ),
        ),
        dmc.Space(h=10),
    ],
    align="center",
    id="main-content",
    style=HIDE,
)


end_content = dmc.Card(
    children=[
        dmc.Container(
            [
                dmc.Text(
                    "Thanks for playing! You've hit the end for today."
                    " Come back tomorrow for more."
                ),
                dmc.Space(h=10),
                html.Div(id="results-div"),
            ],
        ),
        dmc.Space(h=20),
        dmc.Center(
            dmc.Button(
                id="end-button",
                children="Retry",
                rightIcon=DashIconify(icon="carbon:reset-alt"),
                size="md",
                radius="xl",
                color="dark",
            ),
        ),
    ],
    id="end-content",
    withBorder=True,
    shadow="sm",
    radius="md",
    mx=20,
    style=HIDE,
)


app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light", "fontFamily": "'Inter', sans-serif"},
    children=dmc.Center(
        dmc.Stack(
            [
                dcc.Store(id="game-state", storage_type="local"),
                dmc.Space(h=10),
                dmc.Title("Find the AI", style={"height": "10vh"}),
                initial_content,
                content,
                end_content,
                dmc.Space(h=10),
            ],
            align="center",
        ),
    ),
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
)


@callback(
    Output("initial-content", "style"),
    Output("main-content", "style"),
    Output("game-state", "data"),
    Input("acknowledge-button", "n_clicks"),
    State("game-state", "data"),
    prevent_initial_call=True,
)
def load_game_state(acknowledge_clicks, game_state):
    output_initial = HIDE
    output_main = DISPLAY

    time_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    timestamp = (
        time_now if not game_state else game_state.get("created_at", time_now)
    )
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    next_day = dt.date() < datetime.utcnow().date()

    if next_day or not game_state:
        """
        even = pending answer
        odd = result
        """
        game_state = {
            "created_at": datetime.utcnow(),
            "current_frame": 0,
            "question_pairs": get_question_pairs(),
            "results": [None] * QUOTES_PER_DAY,
        }

    return output_initial, output_main, game_state


@callback(
    Output("quote-0", "children"),
    Output("quote-1", "children"),
    Output("quote-0", "cite"),
    Output("quote-1", "cite"),
    Output("card-0", "style"),
    Output("card-1", "style"),
    Output("submit-button", "style"),
    Output("progress-bar", "value"),
    Output("end-content", "style"),
    Output("results-div", "children"),
    Output("game-state", "data", allow_duplicate=True),
    Input("initial-content", "style"),
    Input("submit-button", "n_clicks"),
    Input("end-button", "n_clicks"),
    State("game-state", "data"),
    State("select-0", "checked"),
    State("select-1", "checked"),
    prevent_initial_call=True,
)
def load_next_frame(
    initial_content, submit_clicks, end_clicks, game_state, select_0, select_1
):
    output_cites = [None, None]
    output_card_styles = [CARD_STYLE, CARD_STYLE]
    output_submit_style = no_update
    output_end_style = no_update
    output_results = no_update

    if ctx.triggered_id == "submit-button":
        game_state["current_frame"] += 1
    elif ctx.triggered_id == "end-button":
        game_state["current_frame"] = 0
        game_state["results"] = [None] * QUOTES_PER_DAY
        output_end_style = HIDE
        output_submit_style = DISPLAY

    current_frame = game_state["current_frame"]
    # Out of questions
    if current_frame >= (QUOTES_PER_DAY * 2):
        # Reset game state
        output_quotes = [{"content": no_update}, {"content": no_update}]
        output_card_styles = [HIDE, HIDE]
        output_submit_style = HIDE
        output_end_style = DISPLAY
        output_results = _get_results_div(game_state["results"])

    # Pending answer
    elif game_state["current_frame"] % 2 == 0:
        output_quotes = game_state["question_pairs"][(current_frame // 2)]
    # Result
    else:
        current_pair = game_state["question_pairs"][current_frame // 2]
        output_quotes = current_pair

        if not select_0 and not select_1:
            choice, correct = game_state["results"][current_frame // 2]
        else:
            choice = 0 if select_0 else 1
            correct = current_pair[choice]["type"] == "ai"

        if correct:
            output_card_styles[choice] = {
                **CARD_STYLE,
                "backgroundColor": "#dcfce7",
            }
            game_state["results"][current_frame // 2] = (choice, True)
        else:
            output_card_styles[choice] = {
                **CARD_STYLE,
                "backgroundColor": "#fee2e2",
            }
            game_state["results"][current_frame // 2] = (choice, False)

        for idx in [0, 1]:
            output_cites[idx] = (
                "- ChatGPT"
                if current_pair[idx]["type"] == "ai"
                else f"- {current_pair[idx]['author']}"
            )

    return (
        output_quotes[0]["content"],
        output_quotes[1]["content"],
        output_cites[0],
        output_cites[1],
        output_card_styles[0],
        output_card_styles[1],
        output_submit_style,
        100 * ((current_frame // 2) / QUOTES_PER_DAY),
        output_end_style,
        output_results,
        game_state,
    )


clientside_callback(
    """
    function(
        select_0,
        select_1,
        game_state
    ) {
        var DISPLAY = {
            display: "block",
        };
        var HIDE = {
            display: "none",
        };
        var output_submit = window.dash_clientside.no_update;
        var submit_disabled = false;
        var output_checks = [
            window.dash_clientside.no_update,
            window.dash_clientside.no_update
        ];
        var output_styles = [
            window.dash_clientside.no_update,
            window.dash_clientside.no_update
        ];
        var triggered = dash_clientside.callback_context.triggered[0].prop_id

        if (game_state && game_state.current_frame % 2 === 0) {
            output_submit = "Submit";
            output_styles = [DISPLAY, DISPLAY];
            if (!select_0 && !select_1) {
                submit_disabled = true;
            }
            if (triggered === "select-0.checked") {
                output_checks[0] = select_0;
                output_checks[1] = false;
            } else if (triggered === "select-1.checked") {
                output_checks[0] = false;
                output_checks[1] = select_1;
            }
        } else if (!game_state) {
            // no action needed
        } else {
            output_submit = "Next";
            output_checks = [false, false];
            output_styles = [HIDE, HIDE];
        }

        return [
            output_submit,
            submit_disabled,
            output_checks[0],
            output_checks[1],
            output_styles[0],
            output_styles[1]
        ];
    }
    """,
    Output("submit-button", "children"),
    Output("submit-button", "disabled"),
    Output("select-0", "checked"),
    Output("select-1", "checked"),
    Output("select-0", "style"),
    Output("select-1", "style"),
    Input("select-0", "checked"),
    Input("select-1", "checked"),
    Input("game-state", "data"),
)


def _get_results_div(results: t.List[tuple]):
    num_correct = sum([result[1] for result in results])
    percentage = int((100 * num_correct) / QUOTES_PER_DAY)
    return dmc.Stack(
        [
            dmc.RingProgress(
                sections=[{"value": percentage, "color": "indigo"}],
                label=dmc.Center(dmc.Text(f"{percentage}%", color="indigo")),
            ),
            dmc.Alert(
                f"You got {num_correct} out of {QUOTES_PER_DAY}"
                " quotes correct!",
                title="Congratulations!",
                color="green",
            ),
        ],
        align="center",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
