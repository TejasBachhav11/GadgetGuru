import streamlit as st
import pandas as pd
import joblib
import numpy as np
import re
import time
import os


# Disable Streamlit's file watcher for PyTorch-related files
os.environ["STREAMLIT_WATCHDOG"] = "false"

# Set page configuration
st.set_page_config(
    page_title="GadgetGuru",
    page_icon="logo2.png",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS to style the app like a chat interface
st.markdown(
    """
<style>
    .chat-message {
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .st-emotion-cache-janbn0 {
        background-color: #0a0a0a;
    }

    .chat-message.user {
        background-color: #0a0a0a;
    }
    .chat-message.assistant {
        background-color: #e3f6f5;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .message {
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    .stButton>button {
        border-radius: 20px;
        padding: 0.5rem 1rem;
    }
    div.block-container {
        padding-top: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Load laptop dataset and trained models
@st.cache_resource
def load_data():
    try:
        classified_laptops = pd.read_csv("classified_laptops_output.csv").rename(
            columns=str.strip
        )
        return classified_laptops
    except Exception as e:
        st.error(f"Error loading data or models: {e}")
        # Return empty DataFrame and None for models as fallback
        return pd.DataFrame()


classified_laptops = load_data()

def recommend_laptop(user_prefs):
    budget = user_prefs["budget"]
    categories = user_prefs["categories"]
    travel = user_prefs["travel"]
    battery = user_prefs["battery"]
    brand = user_prefs["brand"]
    flag = "top"
    
    # First filter by budget
    budget_laptops = classified_laptops[classified_laptops["Price"] <= budget]
    
    # Apply brand filter if specified
    if "Any" not in brand:
        brand_laptops = budget_laptops[budget_laptops["Brand"].isin(brand)]
        
        # If brand laptops exist, use them as our primary dataset
        if not brand_laptops.empty:
            filtered_laptops = brand_laptops
        else:
            # No laptops of the requested brand within budget
            filtered_laptops = budget_laptops
            flag = "nobrand"
    else:
        # No brand preference specified
        filtered_laptops = budget_laptops
    
    # Now filter by categories
    filtered_laptops = filtered_laptops[
        filtered_laptops["Laptop Categories"].apply(
            lambda x: any(cat in eval(x) for cat in categories)
        )
    ]
    
    if not filtered_laptops.empty:
        # Apply combined scoring for remaining preferences
        filtered_laptops['combined_score'] = filtered_laptops['Laptop Score']
        
        # Adjust for travel preference (weight)
        if travel == 1:
            weight_max = filtered_laptops['weight'].max()
            weight_min = filtered_laptops['weight'].min()
            weight_range = weight_max - weight_min
            if weight_range > 0:
                filtered_laptops['weight_score'] = (weight_max - filtered_laptops['weight']) / weight_range
                filtered_laptops['combined_score'] += filtered_laptops['weight_score'] * 0.3
        
        # Adjust for battery preference
        if battery == 1:
            battery_max = filtered_laptops['battery capacity'].max()
            battery_min = filtered_laptops['battery capacity'].min()
            battery_range = battery_max - battery_min
            if battery_range > 0:
                filtered_laptops['battery_score'] = (filtered_laptops['battery capacity'] - battery_min) / battery_range
                filtered_laptops['combined_score'] += filtered_laptops['battery_score'] * 0.3
        
        # Get top recommendations
        top_laptops = filtered_laptops.sort_values(by=['combined_score'], ascending=False).head(3)
        return top_laptops, None, flag
    
    else:
        # No laptops match category criteria after brand/budget filtering
        flag = "alternative"
        
        # Check if there are any laptops of the requested brand within budget
        if "Any" not in brand and flag == "nobrand":
            brand_alternatives = budget_laptops[budget_laptops["Brand"].isin(brand)]
            if not brand_alternatives.empty:
                # Return both general alternatives and brand alternatives
                general_alternatives = budget_laptops.sort_values(by=["Laptop Score"], ascending=False).head(3)
                top_brand = brand_alternatives.sort_values(by=["Laptop Score"], ascending=False).head(1)
                return general_alternatives, top_brand, "alternative_with_brand"
        
        # Just return general alternatives
        alternative_laptops = budget_laptops.sort_values(by=["Laptop Score"], ascending=False).head(3)
        if not alternative_laptops.empty:
            return None, alternative_laptops, flag
        else:
            return None, None, None


# Streamlit UI
st.title("Gadget Guru")
st.write("Hey there! Let's find you the perfect laptop—just tell me what you need!")


# Sidebar
with st.sidebar:
    st.image("logo.png")
    st.markdown("# About")
    st.markdown(" **Welcome to Gadget Guru!🚀**")
    st.markdown(
        " Your personal assistant for finding the perfect laptop. No tech jargon—just simple, smart recommendations based on your needs and budget."
    )
    st.markdown("Let's make laptop shopping easy and stress-free!")

    st.markdown(
        "\n  ### Developed by:\n  - [Harshal Kumbhalkar](https://www.linkedin.com/in/justhrk)\n  - [Aryan Dhone](https://www.linkedin.com/in/aryandhone555/)\n  - [Tejas Bachhav](https://www.linkedin.com/in/tejas-bachhav-2403392b8/)\n  - [Rushikesh Fegade](https://www.linkedin.com/in/rushikesh-fegade-508625231/)"
    )

    st.markdown("### What are Laptop categories?\n  👇 Click here to understand")
    with st.popover("Laptops"):
        st.markdown(
            """
### **1️⃣ Gaming Laptops 🎮**  
🔹 **For:** Gamers who want smooth gameplay.  
🔹 **Why?** Super-fast processors, gaming graphics (RTX), and high refresh rate screens.  
🔹 **Example:** Perfect for playing games like GTA V or Call of Duty.  

### **2️⃣ Workstation Laptops 💼**  
🔹 **For:** Professionals using heavy software (video editing, 3D design, coding).  
🔹 **Why?** Powerful processors, special graphics (Quadro), and lots of RAM.  
🔹 **Example:** Great for designers, engineers, or programmers.  

### **3️⃣ Productivity Laptops 📈**  
🔹 **For:** Office workers, students, or anyone who multitasks.  
🔹 **Why?** Fast, lightweight, long battery life.  
🔹 **Example:** Ideal for handling Excel, Zoom calls, or research work.  

### **4️⃣ Business Laptops 🏢**  
🔹 **For:** People who travel a lot and need a reliable laptop.  
🔹 **Why?** Lightweight, strong battery, and built for work on the go.  
🔹 **Example:** Perfect for professionals attending meetings or working remotely.  

### **5️⃣ Budget Laptops 💰**  
🔹 **For:** Anyone looking for an affordable laptop.  
🔹 **Why?** Good for basic work like browsing, watching videos, and light tasks.  
🔹 **Example:** Great for students and casual users.  

### **6️⃣ Basic Computing Laptops 🖥️**  
🔹 **For:** People who need a simple laptop for everyday tasks.  
🔹 **Why?** Cheap, easy to use, and long battery life.  
🔹 **Example:** Best for checking emails, watching YouTube, and using Word.  """
        )


def generate_explanation(user_prefs, laptop_df):
    """Generate a user-friendly explanation of why the recommended laptops match the user's needs,
    with a clear HTML comparison table for better visualization."""
    
    if laptop_df is None or laptop_df.empty:
        return "I couldn't find laptops that perfectly match your requirements."
    
    # Extract key information
    categories = user_prefs["categories"]
    travel_priority = user_prefs["travel"] == 1
    battery_priority = user_prefs["battery"] == 1
    brand_preference = user_prefs["brand"] != "Any" and user_prefs["brand"] is not None
    budget = user_prefs["budget"]
    
    # Start with a personalized greeting
    explanation = "I've selected these laptops specifically for you based on what you told me. Here's why they're a great match:\n\n"
    
    # General category explanation
    if "Gaming" in categories:
        explanation += "🎮 **For Gaming:** These laptops have powerful graphics cards and fast processors that can handle modern games. " 
        explanation += "The high refresh rate displays mean smoother gameplay with less motion blur.\n\n"
    
    if "Workstation" in categories:
        explanation += "💼 **For Professional Work:** These machines offer substantial processing power and RAM to handle demanding software. "
        explanation += "The storage options give you plenty of space for your projects.\n\n"
    
    if "Productivity" in categories:
        explanation += "📊 **For Productivity:** These laptops offer a balance of performance and portability. "
        explanation += "They have enough power to handle multitasking, office applications, and most productivity software.\n\n"
    
    if "Business" in categories:
        explanation += "🏢 **For Business Use:** These laptops offer reliability and performance in a professional package. "
        explanation += "They're built to handle daily business tasks efficiently with good security features.\n\n"
    
    if "Budget" in categories or "Basic Computing" in categories:
        explanation += "💰 **Value for Money:** These laptops offer good performance at reasonable price points, giving you the essential features without unnecessary extras.\n\n"
    
    # Number of laptops to compare
    num_laptops = min(len(laptop_df), 3)
    
    
    # Create rankings to determine strengths
    perf_ranking = laptop_df.iloc[:num_laptops].copy().sort_values('RAM', ascending=False)
    battery_ranking = laptop_df.iloc[:num_laptops].copy().sort_values('battery capacity', ascending=False)
    weight_ranking = laptop_df.iloc[:num_laptops].copy().sort_values('weight')
    price_ranking = laptop_df.iloc[:num_laptops].copy().sort_values('Price')
    
    for i in range(num_laptops):
        laptop = laptop_df.iloc[i]
        strengths = []
        
        # Determine laptop strengths based on rankings
        if laptop['Brand'] == perf_ranking.iloc[0]['Brand'] and laptop['Series'] == perf_ranking.iloc[0]['Series'] and laptop['Item model number'] == perf_ranking.iloc[0]['Item model number']:
            strengths.append("Performance")
            
        if laptop['Brand'] == battery_ranking.iloc[0]['Brand'] and laptop['Series'] == battery_ranking.iloc[0]['Series'] and laptop['Item model number'] == battery_ranking.iloc[0]['Item model number']:
            strengths.append("Battery Life")
            
        if laptop['Brand'] == weight_ranking.iloc[0]['Brand'] and laptop['Series'] == weight_ranking.iloc[0]['Series'] and laptop['Item model number'] == weight_ranking.iloc[0]['Item model number']:
            strengths.append("Portability")
            
        if laptop['Brand'] == price_ranking.iloc[0]['Brand'] and laptop['Series'] == price_ranking.iloc[0]['Series'] and laptop['Item model number'] == price_ranking.iloc[0]['Item model number']:
            strengths.append("Value")
        
        # If no special rankings, add a generic strength
        if not strengths:
            if "Gaming" in categories and ("GTX" in laptop['gpu'] or "RTX" in laptop['gpu']):
                strengths.append("Gaming")
            elif laptop['RAM'] >= 16:
                strengths.append("Multitasking")
            elif laptop['weight'] < 2.0:
                strengths.append("Travel")
            else:
                strengths.append("Everyday Use")

    # Add key strengths section highlighting each laptop's unique advantages
    explanation += "### 🌟 Key Strengths of Each Laptop\n\n"
    
    # For each laptop, highlight its main strengths
    for i in range(num_laptops):
        laptop = laptop_df.iloc[i]
        model_name = f"{laptop['Brand']} {laptop['Series']} {laptop['Item model number']}"
        explanation += f"### {i+1}. {model_name}\n"
        
        strengths = []
        
        # Check if this laptop is best in any category
        if laptop['Brand'] == perf_ranking.iloc[0]['Brand'] and laptop['Series'] == perf_ranking.iloc[0]['Series'] and laptop['Item model number'] == perf_ranking.iloc[0]['Item model number']:
            strengths.append(f"🥇 **Best Performance:** Leads with {laptop['RAM']}GB RAM and {laptop['cpu'][:20]}... processor")
            
        if laptop['Brand'] == battery_ranking.iloc[0]['Brand'] and laptop['Series'] == battery_ranking.iloc[0]['Series'] and laptop['Item model number'] == battery_ranking.iloc[0]['Item model number']:
            strengths.append(f"🥇 **Best Battery Life:** Top battery capacity at {laptop['battery capacity']}mAh")
            
        if laptop['Brand'] == weight_ranking.iloc[0]['Brand'] and laptop['Series'] == weight_ranking.iloc[0]['Series'] and laptop['Item model number'] == weight_ranking.iloc[0]['Item model number']:
            strengths.append(f"🥇 **Most Portable:** Lightest option at only {laptop['weight']} kg")
            
        if laptop['Brand'] == price_ranking.iloc[0]['Brand'] and laptop['Series'] == price_ranking.iloc[0]['Series'] and laptop['Item model number'] == price_ranking.iloc[0]['Item model number']:
            strengths.append(f"🥇 **Most Affordable:** Best price at ₹{laptop['Price']}")
        
        # Add second place mentions
        if len(perf_ranking) > 1 and laptop['Brand'] == perf_ranking.iloc[1]['Brand'] and laptop['Series'] == perf_ranking.iloc[1]['Series'] and laptop['Item model number'] == perf_ranking.iloc[1]['Item model number']:
            strengths.append(f"🥈 **Good Performance:** Second best with {laptop['RAM']}GB RAM")
            
        if len(battery_ranking) > 1 and laptop['Brand'] == battery_ranking.iloc[1]['Brand'] and laptop['Series'] == battery_ranking.iloc[1]['Series'] and laptop['Item model number'] == battery_ranking.iloc[1]['Item model number']:
            strengths.append(f"🥈 **Good Battery Life:** Second best with {laptop['battery capacity']}mAh capacity")
        
        # If no special rankings, add some generic strengths based on specs
        if not strengths:
            if laptop['RAM'] >= 16:
                strengths.append(f"✅ **High RAM:** {laptop['RAM']}GB for smooth multitasking")
            
            if "SSD" in laptop['Hard Disk Description']:
                strengths.append(f"✅ **Fast Storage:** {laptop['Hard Drive Size']} {laptop['Hard Disk Description']} for quick boot and load times")
            
            if laptop['refresh rate'] >= 120:
                strengths.append(f"✅ **Smooth Display:** {laptop['refresh rate']}Hz refresh rate for fluid visuals")
        
        # Add best use case recommendation
        if "Gaming" in categories and ("GTX" in laptop['gpu'] or "RTX" in laptop['gpu']):
            strengths.append(f"👍 **Ideal for:** Gaming, content creation, and demanding tasks")
        elif laptop['RAM'] >= 16 and ("Workstation" in categories or "Productivity" in categories):
            strengths.append(f"👍 **Ideal for:** Professional workloads and productivity")
        elif laptop['weight'] < 2.0 and travel_priority:
            strengths.append(f"👍 **Ideal for:** Frequent travelers and students on the go")
        else:
            strengths.append(f"👍 **Ideal for:** Everyday computing tasks with good overall performance")
        
        # Add the strengths as bullet points
        for strength in strengths:
            explanation += f"- {strength}\n"
        
        explanation += "\n"
    
    # Final recommendations based on user priorities
    explanation += "### 💯 Our Final Recommendations\n\n"
    
    if "Gaming" in categories:
        best_gaming = perf_ranking.iloc[0]
        explanation += f"- **If gaming is your top priority:** Choose the **{best_gaming['Brand']} {best_gaming['Series']} {best_gaming['Item model number']}**\n"
    
    if "Workstation" in categories:
        best_workstation = perf_ranking.iloc[0]
        explanation += f"- **If professional work is your top priority:** Choose the **{best_workstation['Brand']} {best_workstation['Series']} {best_workstation['Item model number']}**\n"
    
    if travel_priority:
        best_travel = weight_ranking.iloc[0]
        explanation += f"- **If portability is your top priority:** Choose the **{best_travel['Brand']} {best_travel['Series']} {best_travel['Item model number']}**\n"
    
    if battery_priority:
        best_battery = battery_ranking.iloc[0]
        explanation += f"- **If battery life is your top priority:** Choose the **{best_battery['Brand']} {best_battery['Series']} {best_battery['Item model number']}**\n"
    
    if "Budget" in categories or "Basic Computing" in categories:
        best_value = price_ranking.iloc[0]
        explanation += f"- **If budget is your top priority:** Choose the **{best_value['Brand']} {best_value['Series']} {best_value['Item model number']}**\n"
    
    # Close with a supportive message
    explanation += "\n🚀 **Bottom Line:** Each laptop has its own strengths that make it suitable for different needs. Use the comparison table and recommendations above to choose the one that best aligns with your most important requirements!"
    
    return explanation

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "budget" not in st.session_state:
    st.session_state.budget = None
if "categories" not in st.session_state:
    st.session_state.categories = []
if "travel" not in st.session_state:
    st.session_state.travel = None
if "battery" not in st.session_state:
    st.session_state.battery = None
if "brand" not in st.session_state:
    st.session_state.brand = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = []


# Function to increment input key to reset the chat input
def reset_input():
    st.session_state.input_key += 1  # Ensure a unique key
    st.rerun()


# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chatbot logic with structured questions
if st.session_state.stage == 0:

    with st.chat_message("assistant"):
        st.write(
            "💰 What's your budget range for the laptop? (Enter in ₹, numbers only) "
        )

    # user_input = st.chat_input("Enter your budget (numbers only, e.g., 50000)", key=f"input_{st.session_state.input_key}")
    user_input = st.chat_input("Enter your budget (numbers only, e.g., 50000)")

    if user_input:
        # Validate numeric input
        if user_input.isdigit():
            if int(user_input) > 14999:
                with st.chat_message("user"):
                    st.write(user_input)
                # Store in session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "💰 What's your budget range for the laptop? (Enter in ₹, numbers only) ",
                    }
                )
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": user_input,
                    }
                )

                budget_value = int(user_input)
                st.session_state.budget = budget_value
                st.session_state.stage = 1
                reset_input()
                st.rerun()
            elif int(user_input) < 15000 and int(user_input) > 0:
                st.warning(
                    f"Unfortunately, ₹{user_input} is too low to purchase a new laptop. Most entry-level laptops start at a higher price. If you're open to increasing your budget, I can help you find the best option within your range."
                )
            else:
                st.error(
                    "⚠ Invalid input. Please enter a valid number (e.g., 50000). Try again."
                )
        else:
            st.error(
                "⚠ Invalid input. Please enter a valid number (e.g., 50000). Try again."
            )


elif st.session_state.stage == 1:
    with st.spinner("Thinking...", show_time=False):
        time.sleep(0.5)

    with st.chat_message("assistant"):
        st.write(
            "🎯 What will you primarily use the laptop for? 🤔💻\n Please select one or more categories that match your needs:"
        )

    # FIX: Use a unique key for chat_input
    with st.chat_message("user"):
        options = [
            "Gaming",
            "Workstation",
            "Productivity",
            "Business",
            "Budget",
            "Basic Computing",
        ]
        selected = st.pills("Laptop Categories", options, selection_mode="multi")

    if selected:
        st.session_state.selected_categories = selected

        if st.button("Confirm"):
            # Add user's message to chat history
            if st.session_state.selected_categories:
                with st.chat_message("user"):
                    st.markdown(", ".join(st.session_state.selected_categories))

                # Store in session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "🎯 What will you primarily use the laptop for? 🤔💻\n Please select one or more categories that match your needs:",
                    }
                )
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": ", ".join(st.session_state.selected_categories),
                    }
                )

            # Store the original user input as the use case
            st.session_state.categories = st.session_state.selected_categories
            st.session_state.stage = 2
            reset_input()
            st.rerun()

elif st.session_state.stage == 2:
    with st.spinner("Writing...", show_time=False):
        time.sleep(0.5)

    with st.chat_message("assistant"):
        st.write("✈️ Do you travel frequently and need a lightweight laptop? ")

    # FIX: Use a unique key for chat_input
    with st.chat_message("user"):
        options = ["Yes", "No"]
        user_input = st.pills("Portability", options, selection_mode="single")

    if user_input:
        # Add user's message to chat history
        with st.chat_message("user"):
            st.write(user_input)

        # Store in session state
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "✈️ Do you travel frequently and need a lightweight laptop? ",
            }
        )
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        if user_input == "Yes":
            st.session_state.travel = 1
        else:
            st.session_state.travel = 0

        st.session_state.stage = 3
        reset_input()
        st.rerun()

elif st.session_state.stage == 3:
    with st.spinner("Thinking...", show_time=False):
        time.sleep(0.5)

    with st.chat_message("assistant"):
        st.write("🔋 Do you need a long battery backup for work or studies?")

    # Fix: Assign a unique key and store selection correctly
    with st.chat_message("user"):
        user_input_battery = st.pills(
            "Long lasting battery",
            ["Yes", "No"],
            selection_mode="single",
            key="battery_selection",
        )

    if user_input_battery:
        with st.chat_message("user"):
            st.write(user_input_battery)

        # Store response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "🔋 Do you need a long battery backup for work or studies?",
            }
        )
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input_battery,
            }
        )

        # Fix: Ensure unique variable usage
        st.session_state.battery = 1 if user_input_battery == "Yes" else 0

        st.session_state.stage = 4
        reset_input()
        st.rerun()


elif st.session_state.stage == 4:
    with st.spinner("Thinking...", show_time=False):
        time.sleep(0.5)

    with st.chat_message("assistant"):
        st.write("🏷️ Do you have a preferred laptop brand?")

    with st.chat_message("user"):
        classified_laptops["Brand"] = classified_laptops["Brand"].str.title()
        unique_brands = classified_laptops["Brand"].unique().tolist()
        options = ["Any"] + unique_brands
        user_input = st.pills("Brand", options, selection_mode="multi")

    if user_input:  # User has submitted something (could be empty string)
        # Add user's message to chat history
        st.session_state.brand = user_input
        if st.button("Confirm"):
            # Add user's message to chat history
            if st.session_state.brand:
                with st.chat_message("user"):
                    st.markdown(", ".join(st.session_state.brand))

                # Store in session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "🏷️ Do you have a preferred laptop brand?",
                    }
                )
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": ", ".join(st.session_state.brand),
                    }
                )

            # Store the original user input as the use case
            st.session_state.stage = 5
            reset_input()
            st.rerun()

elif st.session_state.stage == 5:
    # Process inputs
    user_prefs = {
        "budget": st.session_state.budget,
        "categories": st.session_state.categories,
        "travel": st.session_state.travel,
        "battery": st.session_state.battery,
        "brand": st.session_state.brand,
    }

    response_content = {
        "top": "✅ Based on your requirements, here are my top recommendations:\n\n",
        "nobrand": "🟨 I couldn't find an exact match for your required brand, but here are some alternatives from other brands:",
        "alternative": "🟨 I couldn't find an exact match for your requirements, but here are some alternatives:",
        "alternative_with_brand": "🟨 I couldn't find laptops matching all your requirements, but here are some general recommendations along with an option from your preferred brand:"
    }
    # Recommend a laptop
    best_laptop, alternative_laptops, flag = recommend_laptop(user_prefs)
    with st.spinner(text="Searching for Best Laptop for you...", show_time=False):
            time.sleep(0.5)

    with st.chat_message("assistant"):

        if best_laptop is not None and not best_laptop.empty:
            st.write(response_content[flag])

            for idx, laptop_info in best_laptop.iterrows():
                recommendation = (
                    f"🏷 **Laptop Name**: {laptop_info['Brand']} {laptop_info['Series']} {laptop_info['Item model number']}  \n"
                    f"📺 **Display & Refresh Rate**: {laptop_info['Display']} Pixels | 🔄 {laptop_info['refresh rate']}Hz  \n"
                    f"⚙️ **Processor**: {laptop_info['cpu']}  \n"
                    f"💾 **RAM & Storage**: {laptop_info['RAM']}GB & {laptop_info['Hard Drive Size']} {laptop_info['Hard Disk Description']}  \n"
                    f"🎮 **Graphics**: {laptop_info['gpu']}  \n"
                    f"🖥 **Operating System**: {laptop_info['Operating System']}  \n"
                    f"🔋 **Battery Capacity**: {laptop_info['battery capacity']}mAh  \n"
                    f"⚖️ **Weight**: {laptop_info['weight']} kg  \n"
                    f"💰 **Price**: ₹{laptop_info['Price']}  \n"
                )

                st.markdown(recommendation)
                response_content[flag] += recommendation + "\n"

                # Add Amazon link if available
                if "link" in laptop_info and isinstance(laptop_info["link"], str):
                    st.markdown(
                        f"[👉 View on Amazon]({laptop_info['link']})",
                        unsafe_allow_html=True,
                    )
                    response_content[flag] += f"👉 View on Amazon\n"

                st.markdown("---")

            # Generate user-friendly explanation based on preferences
            st.markdown("### 💡 Why These Laptops Match Your Needs")
            
            explanation = generate_explanation(user_prefs, best_laptop)
            st.markdown(explanation, unsafe_allow_html=True)
            response_content[flag] += "\n\n### 💡 Why These Laptops Match Your Needs\n" + explanation

            # Append to messages - only once
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_content[flag],
                }
            )

        elif alternative_laptops is not None and not alternative_laptops.empty:
            st.write(response_content[flag])

            for idx, laptop_info in alternative_laptops.iterrows():
                recommendation = (
                    f"🏷 **Laptop Name**: {laptop_info['Brand']} {laptop_info['Series']} {laptop_info['Item model number']}  \n"
                    f"📺 **Display & Refresh Rate**: {laptop_info['Display']} Pixels | 🔄 {laptop_info['refresh rate']}Hz  \n"
                    f"⚙️ **Processor**: {laptop_info['cpu']}  \n"
                    f"💾 **RAM & Storage**: {laptop_info['RAM']}GB & {laptop_info['Hard Drive Size']} {laptop_info['Hard Disk Description']}  \n"
                    f"🎮 **Graphics**: {laptop_info['gpu']}  \n"
                    f"🖥 **Operating System**: {laptop_info['Operating System']}  \n"
                    f"🔋 **Battery Capacity**: {laptop_info['battery capacity']}mAh  \n"
                    f"⚖️ **Weight**: {laptop_info['weight']} kg  \n"
                    f"💰 **Price**: ₹{laptop_info['Price']}  \n"
                )

                st.markdown(recommendation)
                response_content[flag] += recommendation + "\n"

                # Add Amazon link if available
                if "link" in laptop_info and isinstance(laptop_info["link"], str):
                    st.markdown(
                        f"[👉 View on Amazon]({laptop_info['link']})",
                        unsafe_allow_html=True,
                    )
                    response_content[flag] += f"👉 View on Amazon\n"

                st.markdown("---")

            # Generate user-friendly explanation for alternative laptops
            st.markdown("### 💡 Why These Alternatives Might Work For You")
            
            explanation = generate_explanation(user_prefs, alternative_laptops)
            st.markdown(explanation, unsafe_allow_html=True)
            response_content[flag] += "\n\n### 💡 Why These Alternatives Might Work For You\n" + explanation

            # Append to messages - only once
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_content[flag],
                }
            )
        else:
            st.error(
                "🔴 Sorry, I couldn't find any laptops matching your criteria. Please try adjusting your budget or requirements."
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Sorry, I couldn't find any laptops matching your criteria. Please try adjusting your budget or requirements.",
                }
            )

    if st.button("Start New Search"):
        # Clear all session state variables including chat messages
        st.session_state.clear()

        # Reinitialize necessary variables
        st.session_state.stage = 0
        st.session_state.messages = []  # Clear chat history

        st.rerun()
