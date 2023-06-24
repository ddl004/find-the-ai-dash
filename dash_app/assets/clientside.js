const QUOTES_PER_DAY = 10;
const DISPLAY = {
    display: "block",
};
const HIDE = {
    display: "none",
};
const CARD_STYLE = {
    minHeight: "32vh"
};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        load_next_frame_function: function load_next_frame(
            initial_content, submit_clicks, end_clicks, game_state, select_0, select_1
        ) {
            const triggered = dash_clientside.callback_context.triggered[0].prop_id

            var output_cites = [null, null];
            var output_card_styles = [CARD_STYLE, CARD_STYLE];
            var output_quotes = [{
                content: null
            }, {
                content: null
            }];
            var output_submit_style = window.dash_clientside.no_update;
            var output_end_style = window.dash_clientside.no_update;

            // Pending answer
            if (triggered === "submit-button.n_clicks") {
                game_state.current_frame += 1;
            // Reset game state
            } else if (triggered === "end-button.n_clicks") {
                game_state.current_frame = 0;
                game_state.results = new Array(QUOTES_PER_DAY).fill(null);
                output_end_style = HIDE;
                output_submit_style = DISPLAY;
            }

            // Out of questions
            var current_frame = game_state.current_frame
            var current_pair = game_state.question_pairs[~~(current_frame / 2)];
            if (current_frame >= QUOTES_PER_DAY * 2) {
                // Reset game state
                output_card_styles = [HIDE, HIDE];
                output_submit_style = HIDE;
                output_end_style = DISPLAY;
            }
            // Pending answer
            else if (current_frame % 2 === 0) {
                output_quotes = current_pair;
            }
            // Result
            else {
                output_quotes = current_pair;

                let choice, correct;
                if (!select_0 && !select_1) {
                    [choice, correct] = game_state.results[~~(current_frame / 2)];
                // User is correct if they chose the AI generated quote
                } else {
                    choice = select_0 ? 0 : 1;
                    correct = current_pair[choice].type === "ai";
                }

                if (correct) {
                    output_card_styles[choice] = {
                        ...CARD_STYLE,
                        // Green
                        backgroundColor: "#dcfce7"
                    };
                    game_state.results[~~(current_frame / 2)] = [choice, true];
                } else {
                    output_card_styles[choice] = {
                        ...CARD_STYLE,
                        // Red
                        backgroundColor: "#fee2e2"
                    };
                    game_state.results[~~(current_frame / 2)] = [choice, false];
                }

                for (let idx of [0, 1]) {
                    output_cites[idx] = current_pair[idx].type === "ai" ?
                        "- ChatGPT" :
                        "- " + current_pair[idx].author;
                }
            }

            return [
                output_quotes[0]?.content,
                output_quotes[1]?.content,
                output_cites[0],
                output_cites[1],
                output_card_styles[0],
                output_card_styles[1],
                output_submit_style,
                100 * (current_frame / (QUOTES_PER_DAY * 2)),
                output_end_style,
                game_state
            ];
        },
        update_button_state_function: function update_button_state(
            select_0,
            select_1,
            game_state
        ) {
            const triggered = dash_clientside.callback_context.triggered[0].prop_id
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
        },
    }
});
