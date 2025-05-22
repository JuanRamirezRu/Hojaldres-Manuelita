#Para usar stremalit y tener la app web
import streamlit as st
#Para usar archivos JSON y guardar/cargar información
import json
import os
#Ruta donde se guardará el menú
ARCHIVO_JSON = "menu_data.json"
#Cargar datos desde el archivo JSON (si existe)
def cargar_menu():
    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
#Guardar el menú actual en el archivo JSON
def guardar_menu(menu):
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)
#Selección de modo de uso (administrador/cliente)
st.sidebar.title("Selección modo de uso")
modo = st.sidebar.radio("¿Qué deseas hacer?", ["Cliente", "Administrador"])


#MODO CLIENTE
if modo == "Cliente":
    #Título de la sección
    st.title("Hojaldres Manuelita")
    st.header("Menú")
    #Lectura de datos (verifica los datos guardados del menú)
    menu = cargar_menu()

    if not menu:
        st.info("El menú no ha sido definido.")
    #Filtro de productos
    else:
        tipo = st.selectbox("Filtrar por tipo", ["Todos", "Postre", "Hojaldre", "Bebida"])
        if tipo != "Todos":
            menu = [p for p in menu if p["Tipo"] == tipo]
        #Visibilidad del menú (imagen, datos)
        for producto in menu:
            col_img, col_datos = st.columns([1, 4])

            with col_img:
                if producto.get("Imagen") and os.path.exists(producto["Imagen"]):
                    st.image(producto["Imagen"], width=150)
                else:
                    st.write(":camera: Sin imagen")

            with col_datos:
                descripcion = f"<br><em>{producto['Descripción']}</em>" if producto.get("Descripción") else ""
                st.markdown(f"""
                    <div style='font-size:18px'>
                        <strong>{producto['Nombre']}</strong><br>
                        Tipo: <em>{producto['Tipo']}</em><br>
                        Precio: ${producto['Precio']:,.2f}{descripcion}
                        <hr>
                    </div>
                """, unsafe_allow_html=True)


#MODO ADMINISTRADOR
elif modo == "Administrador":
    st.subheader("Panel del administrador")
    #Solicitud de contraseña
    password = st.sidebar.text_input("Contraseña", type="password")
    if password != "123":
        st.warning("🔐 Ingresa la contraseña correcta para acceder.")
        st.stop()
    #Título de la sección
    st.title("Gestor de Menús")
    st.subheader("Agrega tus postres y bebidas al menú")
    #Cargar o inicializar menú en memoria
    if "menu" not in st.session_state:
        st.session_state.menu = cargar_menu()
    #Formulario para ingresar productos
    with st.form("formulario_producto"):
        nombre = st.text_input("Nombre del producto")
        tipo = st.selectbox("Tipo", ["Postre", "Hojaldre", "Bebida"])
        precio = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
        descripcion = st.text_area("Descripción del producto (opcional)")
        imagen = st.file_uploader("Imagen del producto", type=["png", "jpg", "jpeg"])
        enviar = st.form_submit_button("Agregar al menú")

        if enviar and nombre.strip():
            ruta_imagen = ""
            if imagen:
                nombre_archivo = f"{nombre.strip().replace(' ', '_').lower()}.{imagen.type.split('/')[-1]}"
                ruta_imagen = f"imagenes/{nombre_archivo}"
                with open(ruta_imagen, "wb") as f:
                    f.write(imagen.getbuffer())

            nuevo_producto = {
                "Nombre": nombre.strip(),
                "Tipo": tipo,
                "Precio": precio,
                "Imagen": ruta_imagen,
                "Descripción": descripcion.strip()
            }
            st.session_state.menu.append(nuevo_producto)
            guardar_menu(st.session_state.menu)
            st.success(f"{nombre} agregado al menú.")
    #Mostrar tabla del menú actual
    if st.session_state.menu:
        st.subheader("Menú actual")
        for i, producto in enumerate(st.session_state.menu):
            col_img, col_datos, col_btns = st.columns([1, 4, 1])

            with col_img:
                if producto.get("Imagen") and os.path.exists(producto["Imagen"]):
                    st.image(producto["Imagen"], width=100)
                else:
                    st.write(":camera: Sin imagen")

            with col_datos:
                st.write(f"**{producto['Nombre']}**")
                st.write(f"Tipo: {producto['Tipo']}")
                st.write(f"Precio: ${producto['Precio']:,.2f}")
                if producto.get("Descripción"):
                    st.write(producto["Descripción"])

            with col_btns:
                if st.button("✏️", key=f"editar_img_{i}"):
                    st.session_state.editar_indice = i
                    st.session_state.editando = True
                    st.rerun()
                if st.button("🗑️", key=f"eliminar_{i}"):
                    eliminado = st.session_state.menu.pop(i)
                    guardar_menu(st.session_state.menu)
                    st.warning(f"❌ {eliminado['Nombre']} eliminado del menú.")
                    st.rerun()

        if st.session_state.get("editando"):
            idx = st.session_state.get("editar_indice")
            #Verificación de si el índice sigue siendo válido
            if idx is not None and 0 <= idx < len(st.session_state.menu):
                producto_editado = st.session_state.menu[idx]
            #Edición de imagen
            else:
                st.warning("⚠️ El producto que intentas editar ya no existe.")
                st.session_state.pop("editando", None)
                st.session_state.pop("editar_indice", None)

            st.subheader(f"Editar producto: {producto_editado['Nombre']}")

            if producto_editado.get("Imagen") and os.path.exists(producto_editado["Imagen"]):
                st.image(producto_editado["Imagen"], width=200)
            else:
                st.info("No hay imagen asociada a este producto.")

            nueva_imagen = st.file_uploader("Sube una nueva imagen", type=["jpg", "jpeg", "png"], key="editar_uploader")
            eliminar_img = st.checkbox("Eliminar imagen actual")
            #Edición de descripción
            nueva_descripcion = st.text_area("Editar descripción", value=producto_editado.get("Descripción", ""))
            #Botón de guardar cambios (tanto si se edita imagen como si se edita descripción)
            if st.button("Guardar cambios"):
                #Eliminar imagen actual si así se indica
                if eliminar_img and producto_editado.get("Imagen") and os.path.exists(producto_editado["Imagen"]):
                    os.remove(producto_editado["Imagen"])
                    producto_editado["Imagen"] = ""
                #Guardar nueva imagen si se sube
                if nueva_imagen:
                    nombre_archivo = f"{producto_editado['Nombre'].strip().replace(' ', '_').lower()}.{nueva_imagen.type.split('/')[-1]}"
                    ruta_imagen = f"imagenes/{nombre_archivo}"
                    with open(ruta_imagen, "wb") as f:
                        f.write(nueva_imagen.getbuffer())
                    producto_editado["Imagen"] = ruta_imagen

                producto_editado["Descripción"] = nueva_descripcion.strip()
                st.session_state.menu[idx] = producto_editado
                guardar_menu(st.session_state.menu)
                st.success("✅ Cambios guardados.")
                del st.session_state.editando
                del st.session_state.editar_indice
                st.rerun()
    else:
        st.info("Aún no hay productos en el menú.")
