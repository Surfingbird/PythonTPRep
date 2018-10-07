def GetContextInfo(Nodes, i, before, after, ListOfMatchedEl):

    StringNumbValue = []

    LeftPart = i - before
    if LeftPart < 0:
        LeftPart = 0

    for j in range (LeftPart, i):
        new_dict = []
        new_dict.append(j)
        new_dict.append(Nodes[j])
        StringNumbValue.append(tuple(new_dict))

    ListOfMatchedEl.append(i)
    m_el = []
    m_el.append(i)
    m_el.append(Nodes[i])
    StringNumbValue.append(tuple(m_el))

    RightPart = i + after + 1

    if RightPart > len(Nodes):
        RightPart = len(Nodes)

    for j in range(i + 1, RightPart):
        new_dict = []
        new_dict.append(j)
        new_dict.append(Nodes[j])
        StringNumbValue.append(tuple(new_dict))

    return StringNumbValue
