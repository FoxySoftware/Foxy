from base_class.os_env_collector_folders import EnvFolders
from base_class.link_keys import Link

link_image_color_area_file = Link.create_link_key(type=Link.LINK_IMAGE_SETTING, folder=EnvFolders.HSV_COLOR_AREA)
link_folder_color_area = Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.HSV_COLOR_AREA)

link_screen_recording_file = Link.create_link_key(type=Link.LINK_VIDEO, folder=EnvFolders.SCREEN_RECORDING)
link_video_source_file = Link.create_link_key(type=Link.LINK_VIDEO, folder=EnvFolders.VIDEO_SOURCE)

link_folder_start_trigger =Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.START_SESSION_TRIGGER_IMAGE)
link_folder_end_trigger =Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.END_SESSION_TRIGGER_IMAGE)
link_folder_list_trigger =Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.LIST_TRIGGER_IMAGES)

link_folder_area_interest =Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.INTEREST_TRIGGER_AREA)
link_folder_area_change_comparison =Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.COMPARISON_AREA)

link_folder_video_source = Link.create_link_key(type=Link.LINK_FOLDER, folder=EnvFolders.VIDEO_SOURCE)


help_resolution_and_video_recording = {
    "step_0_title_ES": "Selección de la resolución de la pantalla virtual",
    "step_0_title_EN": "Selection of Virtual Screen Resolution",
    "step_0_title_PT": "Seleção da Resolução da Tela Virtual",
    
    "step_0_description_ES": "Una resolución más baja aumenta los FPS en todos los procesos de detección de imágenes y captura, pero reduce la precisión del reconocimiento óptico de caracteres. Se recomienda una resolución 4K (3840x2160) para la mayoría de los requisitos.",
    "step_0_description_EN": "A lower resolution increases FPS in all image detection and capture processes but reduces the accuracy of optical character recognition. A 4K resolution (3840x2160) is recommended for most requirements.",
    "step_0_description_PT": "Uma resolução mais baixa aumenta os FPS em todos os processos de detecção e captura de imagens, mas reduz a precisão do reconhecimento óptico de caracteres. Uma resolução 4K (3840x2160) é recomendada para a maioria dos requisitos.",
    
    "step_1_title_ES": "Preparación de la Grabación de Pantalla",
    "step_1_title_EN": "Preparing the Screen Recording",
    "step_1_title_PT": "Preparando a Gravação de Tela",
    
    "step_1_description_ES": "Vamos a grabar la pantalla del sitio web seleccionado. Ajusta la duración de la grabación según sea necesario para capturar las imágenes iniciales de interés en el sitio web. Asegúrate de que el tiempo de grabación sea suficiente para capturar toda la información relevante.",
    "step_1_description_EN": "We will record the screen of the selected website. Adjust the recording duration as needed to capture the initial images of interest on the website. Make sure the recording time is sufficient to capture all relevant information.",
    "step_1_description_PT": "Vamos gravar a tela do site selecionado. Ajuste a duração da gravação conforme necessário para capturar as imagens iniciais de interesse no site. Certifique-se de que o tempo de gravação seja suficiente para capturar todas as informações relevantes.",
}

help_video_recording = {
    "step_0_title_ES": "Preparación de la Grabación de Pantalla",
    "step_0_title_EN": "Preparing the Screen Recording",
    "step_0_title_PT": "Preparando a Gravação de Tela",
    
    "step_0_description_ES": "Vamos a grabar la pantalla del sitio web seleccionado. Ajusta la duración de la grabación según sea necesario para capturar las imágenes iniciales de interés en el sitio web. Asegúrate de que el tiempo de grabación sea suficiente para capturar toda la información relevante.",
    "step_0_description_EN": "We will record the screen of the selected website. Adjust the recording duration as needed to capture the initial images of interest on the website. Make sure the recording time is sufficient to capture all relevant information.",
    "step_0_description_PT": "Vamos gravar a tela do site selecionado. Ajuste a duração da gravação conforme necessário para capturar as imagens iniciais de interesse no site. Certifique-se de que o tempo de gravação seja suficiente para capturar todas as informações relevantes.",
}

help_start_trigger_image_web = {
    "step_0_title_ES": "Preparación de la Imagen Indicadora de Inicio de Session",
    "step_0_description_ES": f"Utilizaremos el video para obtener las imágenes (snapshots) necesarias para configurar el sistema. Para extraer estos snapshots, recomendamos utilizar VLC Media Player {link_screen_recording_file}",
    
    "step_1_title_ES": "Selección de la Imagen",
    "step_1_description_ES": "Reproduce el video en VLC Media Player y pausa en el momento exacto donde deseas capturar la imagen que marcará el comienzo del proceso y la sesión. Esta imagen es crucial, ya que desencadenará el inicio de la captura automatizada.",
    
    "step_2_title_ES": "Recorte de la Imagen",
    "step_2_description_ES": "Una vez que hayas capturado la imagen, es posible que necesites recortarla para que solo se incluya la porción específica que sea representativa y única. En Windows, puedes usar Paint para realizar este recorte. Si estás en Mac OS o Linux, utiliza cualquier editor de imágenes disponible en tu sistema que ofrezca funciones similares.",
    
    "step_3_title_ES": "Guardado de la Imagen",
    "step_3_description_ES": f"Guarda la imagen recortada en la carpeta indicada para este propósito. La carpeta para guardar la imagen es: {link_folder_start_trigger}",
    
    "step_0_title_EN": "Start Image Session Indicator Preparation",
    "step_0_description_EN": f"We will use this video to obtain the necessary snapshots to configure the system. To extract these snapshots, we recommend using VLC Media Player {link_screen_recording_file}",

    "step_1_title_EN": "Image Selection",
    "step_1_description_EN": "Play the video in VLC Media Player and pause at the exact moment where you want to capture the image that will mark the start of the process and session. This image is crucial as it will trigger the beginning of the automated capture.",

    "step_2_title_EN": "Image Cropping",
    "step_2_description_EN": "Once you've captured the image, you may need to crop it to include only the specific portion that is representative and unique. On Windows, you can use Paint to perform this cropping. If you're on Mac OS or Linux, use any available image editor that offers similar functions.",
    
    "step_3_title_EN": "Saving the Image",
    "step_3_description_EN": f"Save the cropped image in the folder designated for this purpose. The path to save the image is: {link_folder_start_trigger}",
    
    "step_0_title_PT": "Preparação da Imagem Indicadora de Início de Sessão",
    "step_0_description_PT": f"Usaremos este vídeo para obter as imagens necessárias para configurar o sistema. Para extrair estas imagens, recomendamos usar o VLC Media Player {link_screen_recording_file}",

    "step_1_title_PT": "Seleção da Imagem",
    "step_1_description_PT": "Reproduza o vídeo no VLC Media Player e pause no momento exato em que deseja capturar a imagem que marcará o início do processo e da sessão. Esta imagem é crucial, pois desencadeará o início da captura automatizada.",

    "step_2_title_PT": "Recorte da Imagem",
    "step_2_description_PT": "Depois de capturar a imagem, pode ser necessário recortá-la para incluir apenas a parte específica que seja representativa e única. No Windows, você pode usar o Paint para realizar esse recorte. Se estiver usando Mac OS ou Linux, utilize qualquer editor de imagens disponível no sistema que ofereça funções semelhantes.",
    
    "step_3_title_PT": "Salvar a Imagem",
    "step_3_description_PT": f"Salve a imagem recortada na pasta designada para este fim. O caminho para salvar a imagem é: {link_folder_start_trigger}"
}

help_start_trigger_image_video = {
    "step_0_title_ES": "Preparación de la Imagen Indicadora de Inicio de Session",
    "step_0_description_ES": f"Utilizaremos el video para obtener las imágenes (snapshots) necesarias para configurar el sistema. Para extraer estos snapshots, recomendamos utilizar VLC Media Player {link_video_source_file}",
    
    "step_1_title_ES": "Selección de la Imagen",
    "step_1_description_ES": "Reproduce el video en VLC Media Player y pausa en el momento exacto donde deseas capturar la imagen que marcará el comienzo del proceso y la sesión. Esta imagen es crucial, ya que desencadenará el inicio de la captura automatizada.",
    
    "step_2_title_ES": "Recorte de la Imagen",
    "step_2_description_ES": "Una vez que hayas capturado la imagen, es posible que necesites recortarla para que solo se incluya la porción específica que sea representativa y única. En Windows, puedes usar Paint para realizar este recorte. Si estás en Mac OS o Linux, utiliza cualquier editor de imágenes disponible en tu sistema que ofrezca funciones similares.",
    
    "step_3_title_ES": "Guardado de la Imagen",
    "step_3_description_ES": f"Guarda la imagen recortada en la carpeta indicada para este propósito. La ruta para guardar la imagen es: {link_folder_start_trigger}",
    
    "step_0_title_EN": "Start Image Session Indicator Preparation",
    "step_0_description_EN": f"We will use this video to obtain the necessary snapshots to configure the system. To extract these snapshots, we recommend using VLC Media Player {link_video_source_file}",

    "step_1_title_EN": "Image Selection",
    "step_1_description_EN": "Play the video in VLC Media Player and pause at the exact moment where you want to capture the image that will mark the start of the process and session. This image is crucial as it will trigger the beginning of the automated capture.",

    "step_2_title_EN": "Image Cropping",
    "step_2_description_EN": "Once you've captured the image, you may need to crop it to include only the specific portion that is representative and unique. On Windows, you can use Paint to perform this cropping. If you're on Mac OS or Linux, use any available image editor that offers similar functions.",
    
    "step_3_title_EN": "Saving the Image",
    "step_3_description_EN": f"Save the cropped image in the folder designated for this purpose. The path to save the image is: {link_folder_start_trigger}",
    
    "step_0_title_PT": "Preparação da Imagem Indicadora de Início de Sessão",
    "step_0_description_PT": f"Usaremos este vídeo para obter as imagens necessárias para configurar o sistema. Para extrair estas imagens, recomendamos usar o VLC Media Player {link_video_source_file}",

    "step_1_title_PT": "Seleção da Imagem",
    "step_1_description_PT": "Reproduza o vídeo no VLC Media Player e pause no momento exato em que deseja capturar a imagem que marcará o início do processo e da sessão. Esta imagem é crucial, pois desencadeará o início da captura automatizada.",

    "step_2_title_PT": "Recorte da Imagem",
    "step_2_description_PT": "Depois de capturar a imagem, pode ser necessário recortá-la para incluir apenas a parte específica que seja representativa e única. No Windows, você pode usar o Paint para realizar esse recorte. Se estiver usando Mac OS ou Linux, utilize qualquer editor de imagens disponível no sistema que ofereça funções semelhantes.",
    
    "step_3_title_PT": "Salvar a Imagem",
    "step_3_description_PT": f"Salve a imagem recortada na pasta designada para este fim. O caminho para salvar a imagem é: {link_folder_start_trigger}"
}


help_end_trigger_image = {
    "step_0_title_ES": "Selección y Preparación de la Imagen Indicador de Fin de Session",
    "step_0_description_ES": "Al igual que la imagen de inicio, reproduce el video en VLC Media Player y pausa en el momento exacto donde deseas capturar la imagen que marcará el fin de la sesión. Cuando se cierre la sesión, quedará a la espera de la detección de la imagen de inicio session.",

    "step_1_title_ES": "Recorte de la Imagen",
    "step_1_description_ES": "Una vez que hayas capturado la imagen, es posible que necesites recortarla para que solo se incluya la porción específica que sea representativa y única. En Windows, puedes usar Paint para realizar este recorte. Si estás en Mac OS o Linux, utiliza cualquier editor de imágenes disponible en tu sistema que ofrezca funciones similares.",
    
    "step_2_title_ES": "Guardado de la Imagen",
    "step_2_description_ES": f"Guarda la imagen recortada en la carpeta indicada para este propósito. La carpeta para guardar la imagen es: {link_folder_end_trigger}",
    
    "step_0_title_EN": "End Image Session Indicator Selection and Preparation",
    "step_0_description_EN": "Similar to the start session image, play the video in VLC Media Player and pause at the exact moment where you want to capture the image that will mark the end of the session. When the session ends, it will wait for the detection of the start session image.",

    "step_1_title_EN": "Image Cropping",
    "step_1_description_EN": "Once you've captured the image, you may need to crop it to include only the specific portion that is representative and unique. On Windows, you can use Paint to perform this cropping. If you're on Mac OS or Linux, use any available image editor that offers similar functions.",
    
    "step_2_title_EN": "Saving the Image",
    "step_2_description_EN": f"Save the cropped image in the folder designated for this purpose. The folder to save the image is: {link_folder_end_trigger}",
    
    "step_0_title_PT": "Seleção e Preparação da Imagem de Fim de Sessão",
    "step_0_description_PT": "Semelhante à imagem de início de sessão, reproduza o vídeo no VLC Media Player e pause no momento exato em que deseja capturar a imagem que marcará o fim da sessão. Quando a sessão for encerrada, o sistema aguardará a detecção da imagem de início de sessão.",

    "step_1_title_PT": "Recorte da Imagem",
    "step_1_description_PT": "Depois de capturar a imagem, pode ser necessário recortá-la para incluir apenas a parte específica que seja representativa e única. No Windows, você pode usar o Paint para realizar esse recorte. Se estiver usando Mac OS ou Linux, utilize qualquer editor de imagens disponível no sistema que ofereça funções semelhantes.",
    
    "step_2_title_PT": "Salvar a Imagem",
    "step_2_description_PT": f"Salve a imagem recortada na pasta designada para este fim. O caminho para salvar a imagem é: {link_folder_end_trigger}"
}



help_list_trigger_image = {
    "step_0_title_ES": "Selección y Preparación de las Imágenes de Indicadoras de Capturas",
    "step_0_description_ES": "El proceso es similar al utilizado para obtener las imágenes de inicio y cierre de sesión, con la diferencia de que estas se utilizan para indicar cuándo se debe realizar una captura desde el momento en que se inicia sesión hasta el cierre de la misma.",
    "step_1_title_ES": "Guardado de las Imágenes",
    "step_1_description_ES": f"Guarda las imágenes recortadas en la carpeta indicada para este propósito. La carpeta para guardar las imágenes es: {link_folder_list_trigger}",
    
    "step_0_title_EN": "Selection and Preparation of Capture Images",
    "step_0_description_EN": "The process is similar to the one used to obtain start and end session images, with the difference that these images are used to indicate when a capture should be made from the start of the session until its end.",
    "step_1_title_EN": "Saving the Images",
    "step_1_description_EN": f"Save the cropped images in the designated folder for this purpose. The folder to save the images is: {link_folder_list_trigger}",
    
    "step_0_title_PT": "Seleção e Preparação das Imagens de Captura",
    "step_0_description_PT": "O processo é semelhante ao utilizado para obter as imagens de início e término de sessão, com a diferença de que essas imagens são usadas para indicar quando uma captura deve ser feita desde o início até o final da sessão.",
    "step_1_title_PT": "Salvar as Imagens",
    "step_1_description_PT": f"Salve as imagens recortadas na pasta designada para este fim. O caminho para salvar as imagens é: {link_folder_list_trigger}"
}



help_interest_trigger_area = {
    "step_0_title_ES": "Área de Imágenes Indicadoras de Sesión y Captura",
    "step_0_description_ES": "Utiliza cualquier captura de pantalla del video para señalar dónde podrían aparecer las imágenes de inicio, indicadores capturas y fin de sesión.",
    "step_1_title_ES": "Dibujar un Cuadro o Rectángulo en el Área de Interés",
    "step_1_description_ES": f"Copia el color de la imagen guardada en {link_image_color_area_file} utilizando tu editor de imágenes favorito. En Windows, podrías usar 'Paint'. Una vez seleccionado el color correcto, pinta el área donde podrían aparecer las imágenes seleccionadas previamente. Es importante que el área indicada sea mayor o al menos del tamaño de las imágenes de inicio de sesión, fin de sesión y las imágenes indicadoras de captura.",
    "step_2_title_ES": "Guardado de la Imagen",
    "step_2_description_ES": f"Guarda la imagen en la carpeta indicada para este propósito. La carpeta para guardar la imagen es: {link_folder_area_interest}",
    
   
    "step_0_title_EN": "Session and Capture Indicator Image Area",
    "step_0_description_EN": "Use any screenshot from the video to indicate where the start and end session images, might appear.",
    "step_1_title_EN": "Draw a Square or Rectangle in the Area of Interest",
    "step_1_description_EN": f"Copy the color from the image saved at {link_image_color_area_file}  using your favorite image editor. On Windows, you might use 'Paint'. Once the correct color is selected, paint the area where the previously selected images might appear. It's important that the indicated area is at least the size of the start session, end session, and capture indicator images if they are present.",
    "step_2_title_EN": "Saving the Image",
    "step_2_description_EN": f"Save the image in the folder designated for this purpose. The folder to save the image is: {link_folder_area_interest}",
  
    "step_0_title_PT": "Área de Imagens Indicadoras de Sessão e Captura",
    "step_0_description_PT": "Use qualquer captura de tela do vídeo para indicar onde as imagens de início e fim de sessão podem aparecer.",
    "step_1_title_PT": "Desenhar um Quadrado ou Retângulo na Área de Interesse",
    "step_1_description_PT": f"Copie a cor da imagem salva em {link_image_color_area_file}  usando seu editor de imagens favorito. No Windows, você pode usar o 'Paint'. Uma vez que a cor correta estiver selecionada, pinte a área onde as imagens selecionadas anteriormente podem aparecer. É importante que a área indicada seja pelo menos do tamanho das imagens de início de sessão, fim de sessão e das imagens indicadoras de captura, se estiverem presentes.",
    "step_2_title_PT": "Salvar a Imagem",
    "step_2_description_PT": f"Salve a imagem na pasta designada para este fim. O caminho para salvar a imagem é: {link_folder_area_interest}"
}




help_area_comparison = {
    "step_0_title_ES": "Área de Comparación para la Detección de Cambios",
    "step_0_description_ES": "Utiliza cualquier captura de pantalla del video para marcar la área donde se espera observar cambios. Cuando se detecte un cambio en estas área, se utilizará como señal para realizar una captura de pantalla.",
  
    "step_1_title_ES": "Dibujar un Cuadro o Rectángulo para indicar el Área",
    "step_1_description_ES": f"Copia el color de la imagen guardada en {link_image_color_area_file}  utilizando tu editor de imágenes favorito. En Windows, podrías usar 'Paint'. Una vez seleccionado el color correcto, pinta el área a observar.",
  
    "step_2_title_ES": "Guardado de la Imagen",
    "step_2_description_ES": f"Guarda la imagen en la carpeta indicada para este propósito. La ruta para guardar la imagen es: {link_folder_area_change_comparison}",

    "step_0_title_EN": "Comparison Area for Change Detection",
    "step_0_description_EN": "Use any screenshot from the video to mark the area where changes are expected. When a change is detected in this area, it will be used as a signal to take a screenshot.",
  
    "step_1_title_EN": "Draw a Square or Rectangle to indicate the Area",
    "step_1_description_EN": f"Copy the color from the image saved at {link_image_color_area_file}  using your favorite image editor. On Windows, you might use 'Paint'. Once the correct color is selected, paint the area to be monitored.",
  
    "step_2_title_EN": "Saving the Image",
    "step_2_description_EN": f"Save the image in the designated folder for this purpose. The path to save the image is: {link_folder_area_change_comparison}",

    "step_0_title_PT": "Área de Comparação para Detecção de Mudanças",
    "step_0_description_PT": "Use qualquer captura de tela do vídeo para marcar as área onde se espera observar mudanças. Quando uma mudança for detectada nessas área, ela será usada como sinal para tirar uma captura de tela.",
  
    "step_1_title_PT": "Desenhar um Quadrado ou Retângulo na Área de Interesse",
    "step_1_description_PT": f"Copie a cor da imagem salva em {link_image_color_area_file}  usando seu editor de imagens favorito. No Windows, você pode usar o 'Paint'. Uma vez que a cor correta estiver selecionada, pinte a área a ser monitorada.",
  
    "step_2_title_PT": "Salvar a Imagem",
    "step_2_description_PT": f"Salve a imagem na pasta designada para este fim. O caminho para salvar a imagem é: {link_folder_area_change_comparison}"
}



help_hsv_color_area = {
    "step_0_title_ES": "Configuración del Color para Indicar Áreas",
    "step_0_description_ES": f"Por defecto, el sistema establece un color en HSV (138, 81, 69), equivalente a RGB (34, 177, 76), para detectar un área. Para modificar el color utilizado para indicar un área, reemplaza la imagen en la carpeta {link_folder_color_area} con una nueva imagen que contenga el color deseado.",
    
    "step_1_title_ES": "¿Por qué cambiar el color predeterminado?",
    "step_1_description_ES": "Si en la captura de pantalla que usas para indicar el área hay colores que coinciden con el valor HSV definido para el área, esto podría afectar la detección del área. Otra posible solución es pintar el resto de la imagen de negro.",

    "step_0_title_EN": "Color Configuration for Area Indication",
    "step_0_description_EN": f"By default, the system sets a color in HSV (138, 81, 69), which is equivalent to RGB (34, 177, 76), for detecting an area. To change the color used for indicating an area, replace the image in the {link_folder_color_area} folder with a new image containing the desired color.",
    
    "step_1_title_EN": "Why Change the Default Color?",
    "step_1_description_EN": "If the screenshot you use to indicate the area contains colors that match the HSV value defined for the area, this could affect the area detection. Other possible solution is to paint the rest of the image black.",

    "step_0_title_PT": "Configuração de Cor para Indicação de Áreas",
    "step_0_description_PT": f"Por padrão, o sistema define uma cor em HSV (138, 81, 69), que é equivalente a RGB (34, 177, 76), para detectar uma área. Para modificar a cor usada para indicar uma área, substitua a imagem na pasta {link_folder_color_area} por uma nova imagem contendo a cor desejada.",
    
    "step_1_title_PT": "Por que mudar a cor padrão?",
    "step_1_description_PT": "Se na captura de tela que você usa para indicar a área houver cores que coincidam com o valor HSV definido para a área, isso pode afetar a detecção da área. Otra possível solução é pintar o resto da imagem de preto.",
}


help_video_source = {
    "step_0_title_ES": "Fuente de Video",
    "step_0_description_ES": f"Debe guardar el video en: {link_folder_video_source}  para que el programa pueda detectar y realizar capturas",
    
    "step_0_title_EN": "Video Source",
    "step_0_description_EN": f"You must save the video at: {link_folder_video_source}  so that the program can detect and take snapshots",
    
    "step_0_title_PT": "Fonte de Vídeo",
    "step_0_description_PT": f"Você deve salvar o vídeo em: {link_folder_video_source}  para que o programa possa detectar e capturar imagens.",
}
