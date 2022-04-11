<?xml version="1.1" encoding="utf-8"?>
<xsl:stylesheet version="1.1"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <!--TICKETS -  actions unique pour tout le document (root)-->
    <xsl:template match="tickets">
        <xsl:variable name="size" select="auto" as="string"/>
        <fo:root>

            <fo:layout-master-set>
                <!--fo:simple-page-master master-name="ticket" page-width="120mm" page-height="${size}" margin="5mm"-->
                <fo:simple-page-master master-name="ticket" page-width="120mm" page-height="auto" margin="5mm">
                    <fo:region-body/>
                </fo:simple-page-master>
            </fo:layout-master-set>

            <fo:bookmark-tree>
                <xsl:for-each select="ticket">
                     <xsl:variable name="index" select="position()"/>
                     <fo:bookmark internal-destination="id{$index}">
                         <fo:bookmark-title>Ticket <xsl:value-of select="@date"/></fo:bookmark-title>
                     </fo:bookmark>
                </xsl:for-each>
            </fo:bookmark-tree>

            <fo:page-sequence master-reference="ticket">
                <fo:flow flow-name="xsl-region-body">
                    <xsl:apply-templates/>
                </fo:flow>
            </fo:page-sequence>

        </fo:root>
    </xsl:template>

    <!-- - TICKET - détails de chaque ticket-->
    <xsl:template match="ticket">
        <xsl:variable name="index" select="position() -1"/>
        <fo:table id="id{$index}" break-before="page" table-layout="fixed" width="100%" border="0.5pt solid black" text-align="left" font-family="Helvetica" font-style="normal" font-size="14pt" color="black">
            <fo:table-column column-width="35mm"/>
            <fo:table-column column-width="75mm"/>
            <fo:table-body>
                <fo:table-row>
                    <fo:table-cell padding-left="5pt">
                        <fo:block>Magasin:</fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding-left="5pt" font-weight="bold">
                        <fo:block><xsl:value-of select="@magasin"/></fo:block>
                    </fo:table-cell>
                </fo:table-row>
                <fo:table-row>
                    <fo:table-cell padding-left="5pt">
                        <fo:block>Caisse:</fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding-left="5pt" font-weight="bold">
                        <fo:block><xsl:value-of select="@caisse"/></fo:block>
                    </fo:table-cell>
                </fo:table-row>
                <fo:table-row>
                    <fo:table-cell padding-left="5pt">
                        <fo:block>Transaction:</fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding-left="5pt" font-weight="bold">
                        <fo:block><xsl:value-of select="@transaction"/></fo:block>
                    </fo:table-cell>
                </fo:table-row>
                <fo:table-row>
                    <fo:table-cell padding-left="5pt">
                        <fo:block>Date:</fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding-left="5pt" font-weight="bold">
                        <fo:block><xsl:value-of select="@date"/></fo:block>
                    </fo:table-cell>
                </fo:table-row>
            </fo:table-body>
        </fo:table>

        <fo:table space-before="10pt" table-layout="fixed" width="100%" text-align="left" font-family="Helvetica" font-style="normal" font-size="12pt" color="black">
            <fo:table-column column-width="60mm"/>
            <fo:table-column column-width="15mm"/>
            <fo:table-column column-width="15mm"/>
            <fo:table-column column-width="20mm"/>
            <fo:table-body>
                <xsl:apply-templates/>
                <fo:table-row font-weight="bold">
                    <fo:table-cell number-columns-spanned="3" padding-top="5pt" >
                        <fo:block>Total:</fo:block>
                    </fo:table-cell >
                    <fo:table-cell padding-top="5pt" >
                        <fo:block text-align="right"><xsl:value-of select="format-number(sum(article/prix),'0.00')"/></fo:block>
                    </fo:table-cell>
                </fo:table-row>
                <fo:table-row font-weight="bold" color="green">
                    <fo:table-cell number-columns-spanned="2" padding-top="2pt" >
                        <fo:block>Rabais:</fo:block>
                    </fo:table-cell >
                    <fo:table-cell padding-top="5pt" >
                        <fo:block text-align="right">
                            <xsl:value-of select="format-number(sum(article/rabais),'0.00')"/>
                        </fo:block>
                    </fo:table-cell>
                </fo:table-row>
            </fo:table-body>
        </fo:table>
        
    </xsl:template>

    <!-- - - ARTICLE - détails de chaque article par ticket -->
    <xsl:template match="article">
        <fo:table-row>
            <fo:table-cell>
                <fo:block>- <xsl:value-of select="texte"/></fo:block>
            </fo:table-cell>
            <fo:table-cell >
                <fo:block><xsl:value-of select="quantite"/></fo:block>
            </fo:table-cell>
            <fo:table-cell >
                <fo:block text-align="right">
                    <xsl:if test="rabais &lt; 0">
                        <xsl:value-of select="format-number(rabais,'0.00')"/>
                    </xsl:if>
                </fo:block>
            </fo:table-cell>
            <fo:table-cell >
                <fo:block text-align="right"><xsl:value-of select="format-number(prix,'0.00')"/></fo:block>
            </fo:table-cell>
        </fo:table-row>

    </xsl:template>
</xsl:stylesheet>
