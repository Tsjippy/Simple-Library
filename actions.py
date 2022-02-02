import constants
from functions import show_error_popup, update_borrowed_items_table, select_user, select_item, show_picture, resource_path

def add_entry(type):
    window      = constants.window
    prefix      = type+'_'
    table       = type.capitalize()+'s'

    #Empty all user_ inputs
    for el_key in window.key_dict:
        if isinstance(el_key, str) and el_key.startswith(prefix) and (window[el_key].metadata == None or not 'clear' in window[el_key].metadata):
            window[el_key].update('')

    #remove image
    window[f'change_{prefix}picture'].update('Add a picture')
    source  = resource_path(f'./pictures/{type}s/default.png')

    #change the image
    window[f'{prefix}picture'].update(source=source, size=(constants.im_width, constants.im_height))

    #add new entry to db
    new_id      = constants.db.add_db_entry(table)
    options     = constants.db.fill_selector(f'{type}_selector')

    index       = len(options)-1
    
    #select new entry
    window[f'{prefix}selector'].update(set_to_index=[index], scroll_to_index=index)

    window[f'{prefix}error'].update(f'Fill in the fields to update the new {type}', visible=True)

    # Show details frame
    window[f'{prefix}details_frame'].update(visible=True)

def delete_entry(entry):
    answer= constants.sg.popup_yes_no(
        f'Are you sure you want to delete this {entry}?'
    )

    if entry == 'user':
        table   = 'Users'
        id      = constants.current_user_data['id']
    else:
        table   = 'Items'
        id      = constants.current_item_data['id']

    if answer == 'Yes':
        # Delete from db
        query   = f'DELETE FROM {table} WHERE id={id}'
        constants.db.update_db_data(query)

        # Hide details frame
        constants.window[f'{entry}_details_frame'].update(visible=False)

        # Remove from selector
        constants.db.fill_selector(f'{entry}_selector')

def update_user_name():
    window  = constants.window

    """ Update display name """
    first_name  = window['user_first_name'].Get().capitalize()
    last_name   = window['user_last_name'].Get().capitalize()

    if first_name == '' and last_name == '':
        return

    # get current user list
    values  = window['user_selector'].GetListValues()

    # current selected index
    index   = window['user_selector'].get_indexes()[0]
    
    # Update list options
    values[index]   = first_name+' '+ last_name

    # Update the selector Listbox
    window['user_selector'].update(values=values)

    # Select updated option
    window['user_selector'].update(set_to_index=[index], scroll_to_index=index)

    # Make sure first name is capitalized
    window['user_first_name'].update(first_name)

    # Make sure last name is capitalized
    window['user_last_name'].update(last_name)

    #Save the displayname
    window['user_display_name'].update(first_name+' '+last_name)

    # Refresh window to show changes
    window.refresh()

    constants.db.update_el_in_db('user_first_name')
    constants.db.update_el_in_db('user_last_name')
    constants.db.update_el_in_db('user_display_name')

def update_item_meta(item_key):
    constants.db.update_el_in_db(item_key)

def user_search(value):
    if not value == '':
        query   = f'SELECT * FROM "main"."Users" WHERE display_name LIKE "%{value}%"'
        data    = constants.db.get_db_data(query)
        if not data == [] and len(data) == 1:
            select_user(data[0]['display_name'])

def item_search(value):
    if not value == '':
        query   = f'SELECT * FROM "main"."Items" WHERE title LIKE "%{value}%"'
        data    = constants.db.get_db_data(query)
        if not data == [] and len(data) == 1:
            select_item(data[0]['title'])

def checkout_show_user(user_data):
    constants.current_user_data = user_data
    window  = constants.window
    user_id = user_data['id']
    data    = update_borrowed_items_table(user_id, 'borroweditems_table')

    max_items   = user_data['max_items']
    if len(data) >= max_items:
        window['checkout_user_error'].update(user_data['first_name']+' has loaned the maximum amount of '+ str(max_items) +' items!')
    else:
        window['checkout_user_error'].update('', visible=False)

    # Show user picture
    show_picture('checkout_user_picture', user_data)

    #Show name
    window['checkout_display_name'].update(user_data['display_name'], visible=True)
    window['checkout_user_barcode'].update(user_data['barcode'], visible=True)
    
    # Show frame
    window['checkout_user_frame'].update(visible=True)

    #Clear search input
    window['checkout_user_search'].update('')

    # Set focus to item search
    window['checkout_item_search'].set_focus()

def checkout_show_item(item_data):
    user_data   = constants.current_user_data
    window      = constants.window

    #clear item search
    window['checkout_item_search'].update('')

    show_picture('checkout_item_picture', item_data)

    #Show name
    window['checkout_title'].update(item_data['title'], visible=True)
    window['checkout_author'].update(item_data['author'])
    window['checkout_item_barcode'].update(item_data['barcode'])

    window['checkout_item_frame'].update(visible=True)
    
    #Clear search input
    window['item_search'].update('')
    window['checkout_item_error'].update('', visible=False)

    #check if check out or check in
    query               = 'SELECT * FROM "main"."Items" WHERE linked_to ='+str(user_data['id'])

    data                = constants.db.get_db_data(query)
    
    checkout            = True
    for row in data:
        #current selected barcode is found in the data array of loaned items by this user
        if row['barcode'] == item_data['barcode']:
            # We are returning a book
            checkout = False
            break
    
    first_name  = user_data['first_name']
    title       = item_data['title']
    # Checking out
    if checkout:
        window['check_in_frame'].update(visible     = False)

        #Check if we are allowed to loan more items
        if len(data) < user_data['max_items']:
            #checkout button
            window['check_out'].update(
                f'Loan "{title}" to '+first_name,
                visible     = True
            )

            window['check_out'].set_focus()
            window['check_out'].set_tooltip(f'Check out "{title}" to '+first_name)
            window['check_out'].bind("<Return>", "")
        else:
            show_error_popup(first_name+' has reached the loan limit of '+ str(user_data['max_items']))
    else:
        window['check_out'].update(visible=False)

        window['check_in'].update(
            f'Return "{title}" to the library',
        )
        
        window['extend_loan'].update(
            f'Extend loan for "{title}"',
        )

        window['check_in_frame'].update(
            visible     = True
        )

        window['check_in'].set_focus()
        window['check_in'].set_tooltip(f'Return "{title}" to the library and remove from '+first_name)
        window['check_in'].bind("<Return>", "")

def checkout_hide_entry(type):
    if type == 'user':
        constants.current_user_data=''
    else:
        constants.current_item_data=''

    constants.window[f'checkout_{type}_error'].update('Nothing found (yet)', visible=True)
    
    # hide the  frame
    constants.window[f'checkout_{type}_frame'].update(visible=False)

def checkout_user_search(value):
    #check if number
    if isinstance(value, int) or isinstance(value, str) and value.isnumeric():
        if not value == 0:                    
            data  = constants.db.get_db_data(f'SELECT * FROM "main"."Users" WHERE barcode = "{value}"')
            if not data == [] and not data[0] == None:
                checkout_show_user(data[0])
            else:
                checkout_hide_entry('user')
        else:
            checkout_hide_entry('user')
    #not a number check for name
    else:
        if not value == '':
            query   = f'SELECT * FROM "main"."Users" WHERE display_name LIKE "%{value}%"'
            data    = constants.db.get_db_data(query)
            
            if not data == [] and not data[0] == None:
                if len(data) == 1:
                    checkout_show_user(data[0])
                else:
                    checkout_hide_entry('user')
                    constants.window['checkout_user_error'].update(str(len(data))+' results found, be more specific', visible=True)
            else:
                checkout_hide_entry('user')
        else:
            checkout_hide_entry('user')

def checkout_item_search(value):
    #check if number
    if isinstance(value, int) or isinstance(value, str) and value.isnumeric():
        if not value == 0:                    
            data  = constants.db.get_db_data(f'SELECT * FROM "main"."Items" WHERE barcode = "{value}"')
            if not data == [] and not data[0] == None:
                checkout_show_item(data[0])
            else:
                checkout_hide_entry('item')
        else:
            constants.window['checkout_user_error'].update('', visible=False)
    #not a number check for name
    else:
        if not value == '':
            data  = constants.db.get_db_data(f'SELECT * FROM "main"."Items" WHERE title LIKE "%{value}%"')
            if not data == [] and not data[0] == None:
                if len(data) == 1:
                    checkout_show_item(data[0])
                else:
                    checkout_hide_entry('item')
                    constants.window['checkout_item_error'].update(str(len(data))+' results found, be more specific', visible=True)
            else:
                checkout_hide_entry('item')
        else:
            checkout_hide_entry('item')
            constants.window['checkout_item_error'].update('', visible=False)