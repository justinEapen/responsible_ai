import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any
import random

# Page configuration
st.set_page_config(
    page_title="🤖 Responsible AI Course - Practice Assignment Quiz",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1f77b4;
    }
    .question-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1f77b4;
        color: #333333;
    }
    .question-container h4 {
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .question-container p {
        color: #333333;
        margin-bottom: 1rem;
    }
    .score-display {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .correct-answer {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for 60 seconds to allow for updates
def load_assignments_data():
    """Load the structured assignments data."""
    try:
        with open('all_weeks_assignments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Assignment data file not found. Please ensure 'all_weeks_assignments.json' exists.")
        return None

def display_question(question: Dict[str, Any], question_num: int, total_questions: int):
    """Display a single question with answer options."""
    
    # Clean duplicate options
    if 'options' in question:
        question['options'] = list(dict.fromkeys(question['options']))  # Remove duplicates while preserving order
    
    # Display question number and text without any boxes
    st.markdown(f"**Question {question_num} of {total_questions} ({question['points']} point{'s' if question['points'] > 1 else ''})**")
    st.markdown(f"**{question['question_text']}**")
    
    # Handle different question types with Streamlit components
    selected_value = None
    if question['question_type'] == 'MCQ':
        # Single choice
        options = question['options']
        selected_value = st.radio(
            "Select your answer:",
            options=options,
            key=f"q{question_num}",
            index=None
        )
    
    elif question['question_type'] == 'MSQ':
        # Multiple choice
        st.write("**Select all that apply:**")
        selected_list = []
        for i, option in enumerate(question['options']):
            if st.checkbox(option, key=f"q{question_num}_option_{i}"):
                selected_list.append(option)
        selected_value = selected_list
    
    # Add separator line between questions (always rendered)
    st.markdown("---")
    
    return selected_value

def calculate_score(questions: List[Dict], user_answers: Dict) -> Dict[str, Any]:
    """Calculate the score for the quiz."""
    total_questions = len(questions)
    correct_answers = 0
    total_possible_points = sum(q['points'] for q in questions)
    earned_points = 0
    
    results = []
    
    for i, question in enumerate(questions):
        question_key = f"q{i+1}"
        user_answer = user_answers.get(question_key, None)
        
        if question['question_type'] == 'MCQ':
            is_correct = user_answer == question['correct_answer']
            if is_correct:
                correct_answers += 1
                earned_points += question['points']
            
            results.append({
                'question_num': i + 1,
                'question_text': question['question_text'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'points': question['points']
            })
        
        elif question['question_type'] == 'MSQ':
            correct_answers_list = question.get('correct_answers', [question['correct_answer']])
            user_selected = user_answer if isinstance(user_answer, list) else []
            
            # For MSQ, check if all correct answers are selected and no incorrect ones
            correct_selected = all(opt in user_selected for opt in correct_answers_list)
            no_incorrect = not any(opt in user_selected for opt in question['options'] if opt not in correct_answers_list)
            is_correct = correct_selected and no_incorrect and len(user_selected) > 0
            
            if is_correct:
                correct_answers += 1
                earned_points += question['points']
            
            results.append({
                'question_num': i + 1,
                'question_text': question['question_text'],
                'user_answer': user_selected,
                'correct_answer': correct_answers_list,
                'is_correct': is_correct,
                'points': question['points']
            })
    
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    points_percentage = (earned_points / total_possible_points) * 100 if total_possible_points > 0 else 0
    
    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'percentage': percentage,
        'total_possible_points': total_possible_points,
        'earned_points': earned_points,
        'points_percentage': points_percentage,
        'results': results
    }

def display_results(score_data: Dict[str, Any]):
    """Display the quiz results."""
    
    st.markdown("## 📊 Quiz Results")
    
    # Overall score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Correct Answers",
            value=f"{score_data['correct_answers']}/{score_data['total_questions']}",
            delta=f"{score_data['percentage']:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Points Earned",
            value=f"{score_data['earned_points']}/{score_data['total_possible_points']}",
            delta=f"{score_data['points_percentage']:.1f}%"
        )
    
    with col3:
        grade = "A" if score_data['percentage'] >= 90 else "B" if score_data['percentage'] >= 80 else "C" if score_data['percentage'] >= 70 else "D" if score_data['percentage'] >= 60 else "F"
        st.metric(
            label="Grade",
            value=grade
        )
    
    # Detailed results
    st.markdown("### 📝 Detailed Results")
    
    for result in score_data['results']:
        with st.expander(f"Question {result['question_num']}: {'✅' if result['is_correct'] else '❌'}"):
            st.write(f"**Question:** {result['question_text']}")
            st.write(f"**Your Answer:** {result['user_answer']}")
            st.write(f"**Correct Answer:** {result['correct_answer']}")
            st.write(f"**Points:** {result['points']} point{'s' if result['points'] > 1 else ''}")
            
            if result['is_correct']:
                st.markdown('<div class="correct-answer">✅ Correct!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="incorrect-answer">❌ Incorrect</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">🤖 Responsible AI Course - Practice Assignment Quiz</div>', unsafe_allow_html=True)
    
    # Load data
    data = load_assignments_data()
    if data is None:
        return
    
    # Sidebar for week selection
    st.sidebar.markdown("## 📚 Select Weeks")
    
    available_weeks = [assignment['week'] for assignment in data['assignments']]
    
    # Debug info
    st.sidebar.markdown(f"**Available weeks:** {sorted(available_weeks)}")
    
    selected_weeks = st.sidebar.multiselect(
        "Choose weeks to include in your quiz:",
        options=available_weeks,
        default=available_weeks[:2] if len(available_weeks) >= 2 else available_weeks,
        help="Select one or more weeks to create a custom quiz"
    )
    
    if not selected_weeks:
        st.warning("Please select at least one week to start the quiz.")
        return
    
    # Get questions from selected weeks
    all_questions = []
    week_info = []
    
    for week_num in selected_weeks:
        assignment = next((a for a in data['assignments'] if a['week'] == week_num), None)
        if assignment:
            week_info.append(assignment)
            for question in assignment['questions']:
                question['week'] = week_num
                all_questions.append(question)
    
    if not all_questions:
        st.error("No questions found for the selected weeks.")
        return
    
    # Display selected weeks info in compact format
    st.markdown("### 📋 Selected Weeks")
    
    # Create a compact display using Streamlit columns
    num_cols = min(6, len(week_info))  # Max 6 columns
    cols = st.columns(num_cols)
    
    for i, week in enumerate(week_info):
        with cols[i % num_cols]:
            # Use Streamlit's metric component for compact display
            st.metric(
                label=f"Week {week['week']}",
                value=f"{len(week['questions'])} Q",
                help=f"Week {week['week']}: {len(week['questions'])} questions"
            )
    
    # Show total questions summary
    total_questions = len(all_questions)
    st.markdown(f"**Total Questions:** {total_questions} across {len(selected_weeks)} week{'s' if len(selected_weeks) > 1 else ''}")
    
    # Quiz options
    st.markdown("### ⚙️ Quiz Options")
    col1, _ = st.columns(2)
    
    with col1:
        shuffle_questions = st.checkbox("Shuffle Questions", value=False, help="Randomize the order of questions")
    
    # Shuffle questions if requested
    if shuffle_questions:
        random.shuffle(all_questions)
    
    # Initialize session state
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    
    # Quiz interface
    st.markdown(f"### 📝 Quiz ({len(all_questions)} questions)")
    
    if not st.session_state.quiz_submitted:
        # Display questions
        for i, question in enumerate(all_questions):
            user_answer = display_question(question, i + 1, len(all_questions))
            st.session_state.user_answers[f"q{i+1}"] = user_answer
        
        # Submit button
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
    
    else:
        # Calculate and display results
        score_data = calculate_score(all_questions, st.session_state.user_answers)
        display_results(score_data)
        
        # Reset button
        if st.button("Take Quiz Again", type="secondary", use_container_width=True):
            st.session_state.quiz_submitted = False
            st.session_state.user_answers = {}
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("**Responsible AI Course** - Interactive Assignment Quiz System")

if __name__ == "__main__":
    main()
