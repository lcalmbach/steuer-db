qry = {
    'ma_liste': """SELECT [mitarbeiterID] as id,[nachname] + ' ' + vorname as [name]
      FROM [stata_produkte].[dbo].[Mitarbeiter]
      where vorname is not null
      order by [nachname] , vorname""",

  'project_team':"""
  """,

  'project_team': """SELECT id, [NameKomplett] as [name], mitarbeiterid, rolleid
      ,[Rolle] rolle
      ,coalesce([Bemerkungen],'') as bemerkungen
      FROM [stata_produkte].[dbo].[vMitarbeiter_Aufgabe]
      where aufgabeId = {}
      and vorname is not null""",
  
  'project_list': "SELECT * from vProjektliste where bezeichnung is not null {} order by thema, bezeichnung",

  'project_detail': "SELECT * FROM vProjektDetail WHERE AufgabeID = {}",

  'apps': "SELECT id, name, description, page FROM app order by sortierung", 

  'lookup_list': "SELECT [LookupCodeId] as id,[bezeichnung] as name FROM [stata_produkte].[dbo].[LookupCodes] where [KategorieId] = {} order by sortierung" 
}