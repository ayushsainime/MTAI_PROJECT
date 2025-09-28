import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import streamlit_authenticator as stauth
# from streamlit_authenticator.utilities.hasher import Hasher
from streamlit_card import card
from annotated_text import annotated_text
import pickle
from pathlib import Path
import time
import gspread
import json
from Delete import deletepage
from Issue import issue
from Issue import ret
from Add import addpage
import pandas as pd

st.set_page_config(
    page_title="RFID",
    page_icon="📙"
)

# doing sceret management
credentials_info = st.secrets['service_account']


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

def get_sheet(database):
    if 'sheet_database' not in st.session_state:
        # Authenticate with the Google Sheets API using the downloaded JSON key file
        gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(credentials_info,SCOPE))
        spreadsheet = gc.open('RFID')
        st.session_state['sheet_database'] = spreadsheet
    return st.session_state['sheet_database']

#st.session_state
work = get_sheet("mydb").worksheet("RFID")
credential = get_sheet("mydb").worksheet("Credentials")
first_col = work.col_values(1) # get values of first column(A)


def main():
    
    left_column, right_column = st.columns(2)
    with left_column:
        st.image('logo.png')

    # Display other content in the right column
    with right_column:
        st.write("# Welcome to Inventory Management 👋 ")   
    
    # defining a session state for the cell(id)
    if 'cell' not in st.session_state:
        st.session_state.cell = None  
         
    #------- product search -------
    text_search = st.text_input("Search products", value="") 

    if st.button("Search🔍",key= 'search'):  
        if text_search:
            productlist = work.col_values(2)
            if text_search in productlist:
                product_index = productlist.index(text_search)
                info = work.row_values(product_index+1)

                annotated_text(("**📙**",f"{info[2]}"))
                annotated_text(("**Status :**",f"{info[4]}"))
                
                if work.cell(product_index+1,4).value != None:

                    json_string = work.cell(product_index+1,4).value
                    # Parse the JSON string into a pandas DataFrame
                    df = pd.DataFrame(json.loads(json_string))
                    st.write("Product History")
                    st.dataframe(df, use_container_width=False)
            else: st.error("Product is not present")
        else: st.error("Invalid input😢")                
        
                
        
    left_column, right_column = st.columns(2) 

          
    if left_column.button("Scan"):

        'Scanning in progress...'

        # Add a placeholder>>>
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
        # Update the progress bar with each iteration.
            latest_iteration.text(f'Progress {i+1}%')
            bar.progress(i + 1)
            time.sleep(0.1) 
        st.session_state.cell = work.cell(1,9).value   #cell I1 will store the scan id  
        work.update_cell(1,9,"") 
    


  
    if 'You' not in st.session_state:
        st.session_state.You = ""
        
    if st.session_state.cell != None:
        try:
            index = first_col.index(st.session_state.cell)
            values = work.row_values(index+1)
            #print(values[4])
            st.success('Scan Successful🎉')

            cols = st.columns(2)
            with cols[0]:
                card(
                title="Product",
                text=f"{values[1]}",
                styles=
                    {
                        "card": { 
                            # "width": "100%", # <- make the card use the width of its container, note that it will not resize the height of the card automatically
                            # "height": "200px", # <- if you want to set the card height to 300px
                            "border-radius": "50px",
                            "box-shadow": "0 0 10px rgba(0,0,0,0.5)",  
                            "border": "2px solid #11d632", # Set border color to red (hex value)  
                            "margin-top": "-30px"  # Move the card up by 20 pixels         
                            }
                    },
                )  
            with cols[1]:
                st.write("**_________**")
                annotated_text(("**Id :**" ,f"{values[0]}"))
                annotated_text(("**📙**",f"{values[2]}"))
                annotated_text(("**Status :**",f"{values[4]}"))
                #annotated_text(("**Remarks :**",f"{values[1]}"))
                st.write("**_________**")
                
            #print(work.cell(index+1,4).value) 
            
            #creating History chart
            if work.cell(index+1,4).value != None:

                json_string = work.cell(index + 1, 4).value
                # Parse the JSON string into a pandas DataFrame
                df = pd.DataFrame(json.loads(json_string))
                if st.checkbox("**Product History**",key="hist") or st.session_state.hist: 
                # st.write("History of the product")
                   st.dataframe(df, use_container_width=False)
                            

            else: st.write("Congratulation You are the first user🎉")    
            
            success_slot = st.empty()       
            
            # return & issue 
            if values[4] == "Not Available":
                if st.checkbox( "**Want to return ?**"):
                    remark = st.text_input("Remarks (optional)")
                    st.button("Proceed" ,key ="proceed",on_click = ret, args = (work,index,remark,success_slot))        

            else:
                
                if st.checkbox("**Want to Issue ?**") or st.session_state.You != "": 
                        Name = st.text_input("Your name", key ="You")
                        email = st.text_input("Email id")
                        date = st.date_input("Expected Return Date",value = None)
                        remark = st.text_input("Remarks (optional)")
                        if(Name and email and date):
                           st.button("submit",key = 'submit',on_click = issue,args= (work,index,Name,email,date,remark,success_slot))

        except ValueError:
            st.success("Scan Successful🎉")
            st.warning("Product is not registered, please register first") 
            
    #else:st.error("Scan Failed :cry:") 
    
    
          

def go2page(whichpage):
    st.session_state['current_page'] = whichpage
    
def logout():
    try: 
        # # Clearing session state or redirecting to login
        for key in st.session_state.keys():
            del st.session_state[key]
        st.session_state['current_page'] = 'login'
    except KeyError:
        st.error("Already logged out or session not started.")
    except Exception as err:
        st.error(f'Unexpected exception {err}')
        raise
    
#------User Athentication---------
def login():
    user = credential.col_values(1)
    usernames = credential.col_values(2)
    password = credential.col_values(3)

    hashed_passwords = stauth.Hasher(password).generate()
    if 'authenticator' not in st.session_state:  
        st.session_state["authenticator"] = stauth.Authenticate(user, usernames, hashed_passwords,
        'RFID', 'abcdef', cookie_expiry_days=30)

    name, authentication_status, username = st.session_state["authenticator"].login("Login📝", "main")

    if authentication_status == False:
        st.error("Username/password is incorrect")

    if authentication_status == None:
        st.warning("Please enter your username and password")
        
    if authentication_status: 
       st.session_state['current_page'] = 'main' 
       
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'    
        
if  st.session_state['current_page'] != 'login':            
    st.sidebar.title(f"Hi {st.session_state.name}")    #user name
    with st.sidebar:
        st.button("Home🏡",on_click=go2page,args=['main'])   
        st.button("Add➕",on_click=go2page,args=['add'])
        st.button("Delete➖",on_click=go2page,args=['delete'])
        # to handle cookie error during logout
        # try:
        #     st.session_state["authenticator"].logout("Logout") 
        # except KeyError:
        #         st.session_state['logout'] = True
        #         st.session_state['name'] = None
        #         st.session_state['username'] = None
        #         st.session_state['authentication_status'] = None
        # except Exception as err:
        #     st.error(f'Unexpected exception {err}')
        #     raise Exception(err)  # but not this, let's crash the app
        st.button("Logout👋",on_click=logout)   
        st.markdown("[Feedback](http://wa.me/7076523590?text=Hi%20Soumyadeep%20some%20suggestion)")   
                     
current_page = st.session_state['current_page']
if current_page == 'main':
    main()  
elif current_page == 'login':
    login()
elif current_page == 'add':
    addpage(work)
elif current_page == 'delete':
    deletepage(work)
