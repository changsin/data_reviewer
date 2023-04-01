import datetime
import fnmatch
import json
import shutil

from st_aggrid import AgGrid

from convert_lib import convert_CVAT_to_Form
from menu_dart import MenuDart
from projects_info import Project, ProjectsInfo
from statistics import *

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"
JSON_EXT = ".json"

CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"

SUPPORTED_FORMATS = [CVAT_XML, PASCAL_VOC_XML, COCO_JSON, ADQ_JSON]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.gif"]

PROJECT_COLUMNS = ['id', 'name', 'file_format_id',
                   'total_count', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]


def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def home(menu_dart: MenuDart):
    st.write("DaRT")


def from_file(str_default, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
        file = open(full_path, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(str_default)


def to_file(data, folder, filename):
    """
    save data to path
    """
    full_path = os.path.join(folder, filename)
    with open(full_path, 'w', encoding="utf-8") as json_file:
        json_file.write(data)


def dashboard(menu_dart: MenuDart):
    st.write("Dashboard")

    # This works
    # # Create a sample dataframe
    # df = pd.DataFrame({'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]})
    #
    # # Define a custom HTML template for each row
    # row_template = """
    # <div style="cursor: pointer">
    #   <div>{}</div>
    #   <div>{}</div>
    # </div>
    # """
    #
    # # Display the dataframe using the custom template
    # for index, row in df.iterrows():
    #     st.write(row_template.format(row['Name'], row['Age']), unsafe_allow_html=True)

    st.subheader("**Projects**")
    df_projects = pd.DataFrame(columns=PROJECT_COLUMNS)
    if menu_dart.projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(menu_dart.projects_info.projects)
        df_projects = df_projects[PROJECT_COLUMNS]

    AgGrid(df_projects)

    # # function to handle row clicks
    # # Add a callback function to handle clicks on the rows
    # def on_table_click(event):
    #     if event:
    #         # Get the index of the clicked row
    #         row_index = event['row']
    #
    #         # Get the data in the clicked row
    #         row_data = df_project_table.iloc[row_index]
    #
    #         # Do something with the data (for example, print it to the console)
    #         print('Clicked row:', row_data)
    #
    # table_project.add_rows(on_table_click)
    # st.dataframe(df_project_table)

    st.subheader("**Tasks**")
    json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
                           # os.path.join(os.getcwd(), "data"),
                           ADQ_WORKING_FOLDER,
                           TASKS + JSON_EXT)

    df_tasks = pd.DataFrame(columns=TASK_COLUMNS)
    if len(json_tasks[TASKS]) > 0:
        df_tasks = pd.DataFrame(json_tasks[TASKS])
        df_tasks = df_tasks[TASK_COLUMNS]

    AgGrid(df_tasks)


def generate_file_tree(folder_path, patterns):
    file_tree_to_return = {}
    for root, dirs, files in os.walk(folder_path):
        level = root.replace(folder_path, '').count(os.sep)
        indent = '-' * (level)

        file_info_to_display = dict()
        for pattern in patterns:
            matched = fnmatch.filter([filename.lower() for filename in files], pattern.lower())
            if matched:
                sub_folder = root.replace(folder_path, '')
                if file_info_to_display.get(sub_folder):
                    file_info_to_display[sub_folder] = file_info_to_display[sub_folder] + len(matched)
                else:
                    file_info_to_display[sub_folder] = len(matched)

                if file_tree_to_return.get(root):
                    file_tree_to_return[root].extend(matched)
                else:
                    file_tree_to_return[root] = matched
                # for filename in matched:
                #     if not os.path.isdir(filename):
                #         file_tree_to_return.append(os.path.join(root, filename))

        for folder, count in file_info_to_display.items():
            st.markdown('{}📁({}) {}/'.format(indent, count, folder))

    return file_tree_to_return


def create_projects(menu_dart: MenuDart):
    with st.form("Create A Project"):
        name = st.text_input("**Name:**")
        images_folder = st.text_input("**Images folder:**")
        images_format_type = st.selectbox("**Image file types**",
                                          ["*.jpg *.jpeg *.png *.bmp *.tiff *.gif",
                                           "*.wav",
                                           "*"])
        labels_folder = st.text_input("**Labels folder:**")
        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_FORMATS)
        submitted = st.form_submit_button("Create project")

        if submitted:
            # Do something with the user's inputs
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Images folder:** {images_folder}")
            # get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)
            # show_dir_tree(Path(images_folder))
            # files_tree = generate_file_tree(images_folder)
            # display_file_tree(files_tree, indent=2)
            image_files = generate_file_tree(images_folder, images_format_type.split())

            st.markdown(f"**Labels folder:** {labels_folder}")
            patterns = ["*.xml"]
            if labels_format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = generate_file_tree(labels_folder, patterns)

            project_id = menu_dart.projects_info.get_next_project_id()

            # from_file()
            destination_folder = os.path.join(ADQ_WORKING_FOLDER, str(project_id))
            if not os.path.exists(destination_folder):
                os.mkdir(destination_folder)

            for folder, files in label_files.items():
                for file in files:
                    anno_file = os.path.join(folder, file)
                    if labels_format_type == CVAT_XML:
                        convert_CVAT_to_Form("NN", anno_file,
                                             str(labels_format_type).lower(), destination_folder)
                    elif labels_format_type == ADQ_JSON:
                        ori_folder = os.path.join(destination_folder, "origin")
                        if not os.path.exists(ori_folder):
                            os.mkdir(ori_folder)

                        shutil.copy(anno_file,
                                    os.path.join(ori_folder, os.path.basename(anno_file)))

            new_project = Project(project_id, name, image_files, label_files,
                                  1, 1, str(datetime.datetime.now()))
            # NB: add as a json dict to make manipulating in pandas dataframe easier
            menu_dart.projects_info.add(new_project.to_json())

            to_file(json.dumps(menu_dart.projects_info, default=default, indent=2),
                    ADQ_WORKING_FOLDER,
                    PROJECTS + JSON_EXT)

            dashboard(menu_dart)


def create_tasks(menu_dart: MenuDart):
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def show_statistics(menu_dart: MenuDart):
    selected = None

    if menu_dart.projects_info.num_count > 0:
        df_projects = pd.DataFrame(menu_dart.projects_info.projects)
        df_project_id_names = df_projects[["id", "name"]]

        selected = st.selectbox("Select project",
                                ["{}-{}".format(id, name) for id, name in
                                 df_project_id_names[["id", "name"]].values.tolist()])
    else:
        st.markdown("**No project is created!**")

    if selected:
        id, name = selected.split('-')
        project_selected = menu_dart.projects_info.get_project_by_id(int(id))
        st.markdown("# Image Files Info")
        plot_datetime("### Created date time", project_selected["image_files"])
        plot_file_sizes("### File sizes", project_selected["image_files"])
        plot_aspect_ratios("### Aspect ratios", project_selected["image_files"])

        st.markdown("# Label Files Info")
        plot_datetime("### Created date time", project_selected["label_files"])
        plot_file_sizes("### Label file sizes", project_selected["label_files"])


def start_st():
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    st.sidebar.header("**DaRT** - Data Reviewing Tool")

    json_projects = from_file("{\"num_count\":0,\"projects\":[]}",
                              # os.path.join(os.getcwd(), "data"),
                              ADQ_WORKING_FOLDER,
                              PROJECTS + JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    menu_dart = MenuDart(projects_info=projects_info)

    menu = {
        "Home": lambda: home(menu_dart),
        "Dashboard": lambda: dashboard(menu_dart),
        "Create Projects": lambda: create_projects(menu_dart),
        "Create Tasks": lambda: create_tasks(menu_dart),
        "Show Statistics": lambda: show_statistics(menu_dart),
    }

    # Create a sidebar with menu options
    selected = st.sidebar.selectbox("Select an option", list(menu.keys()))

    if selected:
        # Call the selected method based on the user's selection
        menu[selected]()


if __name__ == '__main__':
    # dashboard()
    start_st()
    # json_projects = load_projects("{\"num_count\":0,\"projects\":[]}",
    #                               os.path.join(os.getcwd(), "data"),
    #                               "project-sample1.json")
    # print(pd.DataFrame(json_projects["projects"]))
    # json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
    #                         os.path.join(os.getcwd(), "data"),
    #                        "task-sample1.json")
    # df_tasks = pd.DataFrame(json_tasks["tasks"])
    # print(df_tasks[['id', 'name', "project_id"]])