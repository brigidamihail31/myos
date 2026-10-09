<mxfile host="app.diagrams.net" modified="2025-01-01T00:00:00.000Z"
        agent="MyOS" version="24.0.0" type="device">
  <diagram id="myos-arch" name="MyOS Architecture">
    <mxGraphModel dx="900" dy="700" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1"
                  page="1" pageScale="1" pageWidth="827" pageHeight="1169"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Заголовок -->
        <mxCell id="title" value="Архитектура учебной операционной системы"
                style="text;html=1;strokeColor=none;fillColor=none;align=center;
                       verticalAlign=middle;whiteSpace=wrap;rounded=0;
                       fontSize=16;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="240" y="20" width="360" height="30" as="geometry"/>
        </mxCell>

        <!-- shell.py -->
        <mxCell id="shell" value="shell.py (оболочка)"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="320" y="80" width="200" height="50" as="geometry"/>
        </mxCell>

        <!-- syscalls.py -->
        <mxCell id="syscalls" value="syscalls.py"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="320" y="170" width="200" height="50" as="geometry"/>
        </mxCell>

        <!-- kernel.py -->
        <mxCell id="kernel" value="kernel.py (ядро)"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;
                       strokeColor=#d79b00;fontSize=12;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="320" y="260" width="200" height="50" as="geometry"/>
        </mxCell>

        <!-- scheduler.py -->
        <mxCell id="scheduler" value="scheduler.py"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="60" y="380" width="160" height="50" as="geometry"/>
        </mxCell>

        <!-- memory.py -->
        <mxCell id="memory" value="memory.py"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="240" y="380" width="160" height="50" as="geometry"/>
        </mxCell>

        <!-- fs.py -->
        <mxCell id="fs" value="fs.py"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="420" y="380" width="160" height="50" as="geometry"/>
        </mxCell>

        <!-- auth.py -->
        <mxCell id="auth" value="auth.py"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;
                       strokeColor=#6c8ebf;fontSize=12;"
                vertex="1" parent="1">
          <mxGeometry x="600" y="380" width="160" height="50" as="geometry"/>
        </mxCell>

        <!-- db.py -->
        <mxCell id="db" value="db.py (SQLite)"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;
                       strokeColor=#82b366;fontSize=12;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="320" y="510" width="200" height="50" as="geometry"/>
        </mxCell>

        <!-- Стрелки -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="shell" target="syscalls">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="syscalls" target="kernel">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="kernel" target="scheduler">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="kernel" target="memory">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="kernel" target="fs">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="kernel" target="auth">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="scheduler" target="db">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="memory" target="db">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="fs" target="db">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <mxCell id="e10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;
                html=1;endArrow=block;endFill=1;"
                edge="1" parent="1" source="auth" target="db">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
