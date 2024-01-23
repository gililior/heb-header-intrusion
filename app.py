
import gspread
import streamlit as st
import pandas as pd
import random


INSTRUCTIONS = """Below are 10 headers from different legal verdict.\n
9 of them belong to the same group, and one is an intruder.\n
You are asked to identify the intruder. 
If you are not sure, or you believe that there is more than one sentence that does not belong to 
the group of all others, please mark all of the candidates (try to mark as few candidates as possible).\n"""
PATH_TO_EXPERIMENTS = "heb_ver_intruder_experiment.csv"
columns = ["WorkerId", "sample_index_in_input_csv", "Input.in_test_intruder_location", "Answer.answers.0","Answer.answers.1","Answer.answers.2","Answer.answers.3	Answer.answers.4	Answer.answers.5	Answer.answers.6	Answer.answers.7	Answer.answers.8	Answer.answers.9	Answer.description	Approve	Reject"]


def record_name():
    if len(st.session_state.username_box) == 0:
        st.error('You must enter a valid username')
    else:
        st.session_state.username = st.session_state.username_box
        next_page()


def record_sample_index():
    next_row_index = len(st.session_state.ws.col_values(1)) + 1
    st.session_state.ws.update(values=[[st.session_state.username]], range_name='A' + str(next_row_index))
    st.session_state.ws.update(values=[[st.session_state.current_sample_index]], range_name='B' + str(next_row_index))
    st.session_state.next_row_index = next_row_index


def record_answer():
    ind = st.session_state.next_row_index
    intruder_location = st.session_state.df.iloc[st.session_state.current_sample_index]["in_test_intruder_location"]
    st.session_state.ws.update(values=[[str(intruder_location)]], range_name='C' + str(ind))
    for i in range(10):
        st.session_state.ws.update(values=[[st.session_state[f"Answers.answer.{i}"]]],
                                   range_name=chr(ord('D') + i) + str(ind))


def get_next_sample():
    indices = st.session_state.ws.col_values(2)
    indices = set([int(x) for x in indices[1:]])
    all_input_indices = set(st.session_state.df.index)
    to_choose = list(all_input_indices - indices)
    st.session_state.current_sample_index = random.choice(to_choose)


def next_page():
    st.session_state.cur_page += 1
    get_next_sample()
    record_sample_index()


def hello_page():
    st.header('Header Intrusion')
    st.markdown('Hello! Please enter your name')
    st.text_input('Username', key='username_box')

    st.button('Next', key='next_button0', on_click=record_name)


def init(ws_name):
    with st.expander("❔ See Instructions"):
        st.write(INSTRUCTIONS)
    if "ws" not in st.session_state:
        gc = gspread.service_account_from_dict(st.secrets["credentials"])
        sh = gc.open("cluster-annotation")
        st.session_state.ws = sh.worksheet(ws_name)
        st.session_state.cur_page = 0
        st.session_state.df = load_csv()
        st.session_state.progress = 0


@st.cache_data
def load_csv():
    return pd.read_csv(PATH_TO_EXPERIMENTS)


def main():
    st.title("Header Intrusion")
    st.markdown("Please select the header that does not belong to the group of all others. If you are uncertain, you can mark more than one option, but please try to mark as few candidates as possible.")

    my_bar = st.progress(st.session_state.progress)
    df = st.session_state["df"]

    if st.button('submit'):
        # check that at least one checkbox is checked
        if not any([st.session_state[f"Answers.answer.{i}"] for i in range(10)]):
            st.error('You must check at least one checkbox')
        else:
            record_answer()
            get_next_sample()
            record_sample_index()
            st.session_state.progress += 1
            my_bar.progress(st.session_state.progress)
    current_row = df.iloc[st.session_state.current_sample_index]
    # for each column in the row, set a checkbox
    for i in range(10):
        st.checkbox(label=current_row[f"sentence_{i}_text"], value=False, key=f"Answers.answer.{i}")


if __name__ == '__main__':
    init("heb_ver_intruder_experiment")
    if st.session_state.cur_page == 0:
        hello_page()
    else:
        main()
