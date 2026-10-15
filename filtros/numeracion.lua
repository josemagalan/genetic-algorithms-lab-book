--[[
Numeración de los ejemplos y ejercicios, y referencias a ellos.

Quarto numera capítulos, secciones y figuras, pero no estas cajas por sección.
filtros/indices.py (pre-render) calcula los números en _numeracion.json y este
filtro los escribe:

  - En el título de cada caja .ejemplo o .ejercicio con identificador:
      title="Ejemplo reproducible · Cuatro torneos"  →  «Ejemplo reproducible 5.2 · Cuatro torneos»
  - En los enlaces vacíos a una caja, en este capítulo o en otro:
      ejemplo [](#ejemplo-seleccion-torneo)  →  ejemplo 5.2
  - En los enlaces vacíos con la clase .capitulo, que dan el número de capítulo
    de una sección y enlazan a esa sección:
      capítulo [](#sec-cruce-permutaciones){.capitulo}  →  capítulo 6

Además deja anclas con los identificadores anteriores a la numeración automática,
para que no se rompan los enlaces que ya apuntaban a una sección o a una caja:
antes de cada sección, el suyo sin prefijo (sec-seleccion-ruleta conserva #ruleta),
y antes de cada caja, el de su número (#ejemplo-5-3).
]]

local datos = nil
local archivo = nil
local prefijo = nil   -- "sec-<capítulo>-"

local function leer_datos()
  local dir = (quarto.project and quarto.project.directory) or "."
  local ruta = pandoc.path.join({ dir, "_numeracion.json" })
  local f = io.open(ruta, "r")
  if not f then
    error("numeracion.lua: falta " .. ruta .. ". Lo genera filtros/indices.py en el pre-render; " ..
      "ejecuta «quarto render» o «python3 filtros/indices.py».")
  end
  local texto = f:read("a")
  f:close()
  datos = pandoc.json.decode(texto, false)
  archivo = pandoc.path.filename(quarto.doc.input_file or "")
  for id, c in pairs(datos.capitulos) do
    if c.archivo == archivo then prefijo = id .. "-" end
  end
end

local function destino(entrada, id)
  if entrada.archivo == archivo then return "#" .. id end
  return entrada.archivo .. "#" .. id
end

local function avisa(msg)
  if quarto.log and quarto.log.warning then quarto.log.warning(msg) else io.stderr:write(msg .. "\n") end
end

local function numerar_titulo(titulo, numero)
  local pos = titulo:find(" · ", 1, true)
  if pos then return titulo:sub(1, pos - 1) .. " " .. numero .. titulo:sub(pos) end
  return titulo .. " " .. numero
end

local function caja(el)
  if not (el.classes:includes("ejemplo") or el.classes:includes("ejercicio")) then return nil end
  local c = datos.cajas[el.identifier]
  if not c then
    avisa("numeracion.lua: la caja #" .. el.identifier .. " de " .. archivo .. " no está en _numeracion.json")
    return nil
  end
  local titulo = el.attributes["title"]
  if titulo then el.attributes["title"] = numerar_titulo(titulo, c.numero) end
  return el
end

local function enlace(el)
  if #el.content > 0 then return nil end
  local id = el.target:match("#([%w%-_]+)$")
  if not id then return nil end
  if el.classes:includes("capitulo") then
    local s = datos.secciones[id] or datos.capitulos[id]
    if not s then
      avisa("numeracion.lua: [](#" .. id .. "){.capitulo} en " .. archivo .. ": sección desconocida")
      el.content = { pandoc.Str("??") }
      return el
    end
    el.classes = el.classes:filter(function(x) return x ~= "capitulo" end)
    el.content = { pandoc.Str(s.capitulo or s.numero) }
    el.target = destino(s, id)
    return el
  end
  local c = datos.cajas[id]
  if c then
    el.content = { pandoc.Str(c.numero) }
    el.target = destino(c, id)
    return el
  end
  avisa("numeracion.lua: enlace vacío a #" .. id .. " en " .. archivo .. ": no es una caja numerada")
  el.content = { pandoc.Str("??") }
  return el
end

local function ancla_antigua(el)
  if el.level ~= 2 or not prefijo or not quarto.doc.is_format("html") then return nil end
  local id = el.identifier
  if id:sub(1, #prefijo) ~= prefijo then return nil end
  local viejo = id:sub(#prefijo + 1)
  return { pandoc.RawBlock("html", '<span id="' .. viejo .. '" class="ancla-antigua"></span>'), el }
end

return {
  { Pandoc = function(doc) leer_datos(); return nil end },
  {
    Div = caja,
    -- Quarto convierte las cajas en su propio nodo Callout antes de los filtros del
    -- libro; el título llega ya como texto con formato y se numera sin perderlo.
    Callout = function(el)
      local id = el.attr and el.attr.identifier
      local c = id and datos.cajas[id]
      if not c then return nil end
      if el.title then
        -- el número va delante del primer «·» («Ejemplo reproducible 5.2 · …»)
        local hecho = false
        local function numerar(ils)
          if hecho then return nil end
          local nuevo = pandoc.Inlines({})
          for _, x in ipairs(ils) do
            if not hecho and x.t == "Str" and x.text == "·" then
              nuevo:insert(pandoc.Str(c.numero)); nuevo:insert(pandoc.Space()); hecho = true
              if quarto.doc.is_format("html") then
                -- ancla con el número (#ejemplo-5-3), como antes de la numeración automática
                local num = c.tipo .. "-" .. c.numero:gsub("%.", "-")
                nuevo:insert(pandoc.RawInline("html", '<span id="' .. num .. '" class="ancla-antigua"></span>'))
              end
            end
            nuevo:insert(x)
          end
          return nuevo
        end
        el.title = el.title:walk({ Inlines = numerar })
        if not hecho then
          avisa("numeracion.lua: la caja #" .. id .. " no tiene «·» en el título; queda sin número")
        end
      end
      return el
    end,
    Link = enlace,
    Header = ancla_antigua,
  },
}
