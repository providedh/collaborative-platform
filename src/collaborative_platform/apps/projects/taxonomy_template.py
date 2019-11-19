template_string = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Uncertainty Taxonomy for project {}</title>
      </titleStmt>
    </fileDesc>
    <encodingDesc>
      <classDecl>
        <taxonomy>
          <category>
            <catDesc>User recognized uncertainty</catDesc>
            <category xml:id="{}">
              <catDesc>{}</catDesc>
            </category>
            <category xml:id="{}">
              <catDesc>{}</catDesc>
            </category>
            <category xml:id="{}">
              <catDesc>{}</catDesc>
            </category>
            <category xml:id="{}">
              <catDesc>{}</catDesc>
            </category>
          </category>
          <category>
            <catDesc>Machine generated uncertainty</catDesc>
            <category xml:id="algorithmic">
              <catDesc>Algorithmic</catDesc>
            </category>
          </category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
  </teiHeader>
</TEI>"""
