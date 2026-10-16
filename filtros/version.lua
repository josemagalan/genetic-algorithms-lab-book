-- Escribe la versión del libro (libro-version, en _quarto.yml) en la cabecera de cada página,
-- como <meta name="libro-version">, para que comentarios.js la añada al formulario de comentarios.
function Meta(m)
  local v = m["libro-version"]
  if v ~= nil and quarto.doc.is_format("html") then
    local texto = pandoc.utils.stringify(v):gsub('[&"<>]', '')
    quarto.doc.include_text("in-header", '<meta name="libro-version" content="' .. texto .. '">')
  end
  return m
end
