function Para(el)
    local c = el.content
    if #c == 3
        and c[1].t == "Str" and c[1].text == "!include"
        and c[2].t == "Space"
        and c[3].t == "Str"
    then
        local path = c[3].text
        local f = io.open(path, "r")
        if f then
            local content = f:read("*all")
            f:close()
            return pandoc.read(content, "markdown").blocks
        end
    end
end
