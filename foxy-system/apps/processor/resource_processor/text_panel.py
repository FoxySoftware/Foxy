
from base_class.menu_project import ConfigMenuProject
from base_class.sections import ConfigSections

panel_1 = ConfigSections.PROJECT.value
panel_2 = ConfigSections.HSV_COLOR_AREA.value
panel_3 = ConfigSections.AREAS_IMAGE_OCR.value
panel_4 = ConfigSections.AREAS_IMAGE_OCR_LISTED.value
panel_5 = ConfigSections.SECTION_SETTING_AREAS_OCR.value
panel_6 = ConfigSections.PROJECT_SESSION_STATE.value
panel_7 = ConfigSections.TASK_IN_PROGRESS.value
panel_8 = ConfigSections.SUB_IMAGE_TO_REMOVE.value

dict_panel_title_en = {
    f"{panel_1}_EN": "PROJECT OVERVIEW  🗃️ ",
    f"{panel_2}_EN": "AREA COLORS  🟢 ",
    f"{panel_3}_EN": "IMAGE WITH OCR AREAS 🔲 ",
    f"{panel_4}_EN": "IMAGE WITH LISTED OCR AREAS 🔢 ",
    f"{panel_5}_EN": "OCR AREA SETTINGS 🛠️ ",
    f"{panel_6}_EN": "PROJECT SESSION STATE 🚦 ",
    f"{panel_7}_EN": "TASK IN PROGRESS 📈 ", 
    f"{panel_8}_EN": "SUB IMAGES TO REMOVE ⛔", 

}

dict_panel_title_es = {
    f"{panel_1}_ES": "VISIÓN GENERAL DEL PROYECTO  🗃️ ",
    f"{panel_2}_ES": "COLORES DE LAS ÁREAS 🟢 ",
    f"{panel_3}_ES": "IMAGEN CON ÁREAS PARA APLICAR OCR 🔲",
    f"{panel_4}_ES": "IMAGEN CON ÁREAS PARA APLICAR OCR ENUMERADAS 🔢 ",
    f"{panel_5}_ES": "CONFIGURACIONES DE ÁREAS OCR 🛠️",
    f"{panel_6}_ES": "ESTADO DE LA SESIÓN DEL PROYECTO 🚦 ",
    f"{panel_7}_ES": "TAREA EN PROCESO 📈 ", 
    f"{panel_8}_ES": "SUB IMAGENES A REMOVER ⛔", 

}

dict_panel_title_pt = {
    f"{panel_1}_PT": "VISÃO GERAL DO PROJETO 🗃️ ",
    f"{panel_2}_PT": "CORES DAS ÁREAS 🟢 ",
    f"{panel_3}_PT": "IMAGEM COM ÁREAS PARA APLICAR OCR 🔲 ",
    f"{panel_4}_PT": "IMAGEM COM ÁREAS PARA APLICAR OCR ENUMERADAS 🔢 ",
    f"{panel_5}_PT": "CONFIGURAÇÕES DE ÁREA DE OCR 🛠️ ",
    f"{panel_6}_PT": "ESTADO DA SESSÃO DO PROJETO 🚦 ",
    f"{panel_7}_PT": "TAREFA EM ANDAMENTO 📈 ",  
    f"{panel_8}_PT": "SUB IMAGENS A REMOVER ⛔"
}


menu_1 = ConfigMenuProject.AUTOMATIC_OPTION.value
menu_2 = ConfigMenuProject.RELOAD_CONFIG.value
menu_3 = ConfigMenuProject.WELCOME.value
menu_4 = ConfigMenuProject.AREAS_IMAGE_OCR.value
menu_5 = ConfigMenuProject.SETTING_AREAS_OCR.value
menu_6 = ConfigMenuProject.INIT_OCR_PROCESS.value
menu_7 = ConfigMenuProject.MENU_DATA_PROCESS.value
menu_8 = ConfigMenuProject.EXIT.value
menu_9 = ConfigMenuProject.ACTIVATE_GPU.value

dict_menu_panel_en = {    
    f"{menu_1}_EN": "AUTOMATIC OPTION SELECTION 🕹️",
    f"{menu_2}_EN": "RELOAD CONFIGURATION 🔄",
    f"{menu_3}_EN": "MAIN MENU 🏁",
    f"{menu_4}_EN": "IMAGE OCR AREAS MENU 🔲",
    #GPU OPTION
    f"{menu_9}_EN": "ACTIVE GPU OCR ⚙️",
    f"{menu_5}_EN": "OCR AREA CONFIGURATION MENU 🛠️",
    f"{menu_6}_EN": "INITIATE OCR PROCESS 🔍",
    f"{menu_7}_EN": "EXPORT DATA MENU 💾",
    f"{menu_8}_EN": "EXIT 🚪",
}

dict_menu_panel_es = { 
    f"{menu_1}_ES": "SELECCIÓN DE OPCIÓN AUTOMÁTICA 🕹️",
    f"{menu_2}_ES": "RECARGAR CONFIGURACIÓN 🔄",
    f"{menu_3}_ES": "MENÚ PRINCIPAL 🏁",
    f"{menu_4}_ES": "MENÚ DE ÁREAS OCR EN IMÁGENES 🔲",
    #GPU OPTION
    f"{menu_9}_ES": "ACTIVAR GPU OCR ⚙️",
    f"{menu_5}_ES": "MENÚ DE CONFIGURACIÓN DE ÁREAS OCR 🛠️",
    f"{menu_6}_ES": "INICIAR PROCESO DE OCR 🔍",
    f"{menu_7}_ES": "MENÚ DE EXPORTACIÓN DE DATOS 💾",
    f"{menu_8}_ES": "SALIR 🚪",
}

dict_menu_panel_pt = {    
    f"{menu_1}_PT": "SELEÇÃO DE OPÇÃO AUTOMÁTICA 🕹️",
    f"{menu_2}_PT": "RECARREGAR CONFIGURAÇÃO 🔄",
    f"{menu_3}_PT": "MENU PRINCIPAL 🏁",
    f"{menu_4}_PT": "MENU DE ÁREAS OCR EM IMAGENS 🔲",
    #GPU OPTION
    f"{menu_9}_EN": "ACTIVE GPU OCR ⚙️",
    f"{menu_5}_PT": "MENU DE CONFIGURAÇÃO DE ÁREA DE OCR 🛠️",
    f"{menu_6}_PT": "INICIAR O PROCESSO DE OCR 🔍",
    f"{menu_7}_PT": "MENU DE EXPORTAÇÃO DE DADOS 💾",
    f"{menu_8}_PT": "SAIR 🚪",
}


dict_menu_panel = {}
dict_menu_panel.update(dict_menu_panel_en)
dict_menu_panel.update(dict_menu_panel_es)
dict_menu_panel.update(dict_menu_panel_pt)

dict_panel_title = {}
dict_panel_title.update(dict_panel_title_en)
dict_panel_title.update(dict_panel_title_es)
dict_panel_title.update(dict_panel_title_pt)

if __name__ == "__main__":
    RED = '\033[91m'
    RESET = '\033[0m'
    
    def check_dict(dict_source, list_dict_to_check, suffix_dict_source ,suffix_to_check ):
       
        print(f"total_keys EN: {len(dict_source.keys())}")
    
        for i, dict_lang in enumerate(list_dict_to_check):

            for  key, value in dict_source.items():
                cropped_key = key[:-2]
                suffix = key[-2:]
                if suffix != suffix_dict_source:
                    print (f"{RED} The suffix {suffix} is incorret in dict_source key: {key} {RESET}")

                try:
                    dict_lang[f"{cropped_key}{suffix_to_check[i]}"]
                except KeyError as e:
                    print (f"{RED} This {e} key is not present in {suffix_to_check[i]}{RESET}")
                    
            print(f"total_keys {suffix_to_check[i]}: {len(dict_lang.keys())}")
    
    suffix_dict_source = "EN"
    list_suffix_dict_to_check = ["ES", "PT"]

    print("dict_menu_panel_en")
    dict_source = dict_menu_panel_en
    list_dict_to_check = [dict_menu_panel_es, dict_menu_panel_pt]
    check_dict(dict_source, list_dict_to_check,suffix_dict_source ,list_suffix_dict_to_check)
    
    print("dict_panel_title_en")  
    dict_source = dict_panel_title_en
    list_dict_to_check = [dict_panel_title_es, dict_panel_title_pt]
    check_dict(dict_source, list_dict_to_check,suffix_dict_source, list_suffix_dict_to_check)
   
