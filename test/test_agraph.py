import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

nodes = []
edges = []
nodes.append( Node(id="Spiderman",
                   label="Peter Parker",
                   size=25,
                   shape="circularImage",
                   image=f"http://localhost:8090/files?fn=tmp/inv.png", _type="123", _data={"test": "test"})
            ) # includes **kwargs
nodes.append( Node(id="Captain_Marvel",
                   size=25,
                   shape="circularImage",
                   image=f"http://localhost:8090/files?fn=tmp/receipt.png", _type="456", _data={"test999": "test91111"})
            )
edges.append( Edge(source="Captain_Marvel",
                   label="friend_of",
                   target="Spiderman",
                   # **kwargs
                   )
            )

config = Config(width=750,
                height=950,
                directed=True,
                physics=True
                )

return_value = agraph(nodes=nodes,
                      edges=edges,
                      config=config)

# 显示点击的节点信息
if return_value:
    st.write(f"你点击了: {return_value}")