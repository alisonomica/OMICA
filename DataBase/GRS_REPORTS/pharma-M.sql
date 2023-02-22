USE OMICA;
CREATE TABLE `PHARMA-MAN` (
`ID`varchar(13) NOT NULL,
`asparaginase_hypersensitivity` FLOAT(9),
`clozapine-induced_agranulocytosisgranulocytopenia` FLOAT(9),
`drug-induced_stevens-johnson_syndrome` FLOAT(9),
`response_to_antipsychotic_treatment` FLOAT(9),
`response_to_bronchodilator` FLOAT(9)



);

INSERT INTO `PHARMA-MAN`(`ID` , `asparaginase_hypersensitivity` , `clozapine-induced_agranulocytosisgranulocytopenia` , `drug-induced_stevens-johnson_syndrome` , `response_to_antipsychotic_treatment` , `response_to_bronchodilator`) VALUES
('id_136623u67',-0.770885,-0.1766595,1.491946,-1.255177,-0.01691643),
('id_1856ixF05',-0.9812677,0.3463543,2.685502,-0.7567977,0.2093806),
('id_34k3jK350',0.4020803,-0.4589267,-1.776771,-0.7318062,-0.38305),
('id_361Z6LS50',-1.015404,-0.4780732,-1.193556,0.2953357,0.2726902),
('id_6N2f72J26',-1.015404,-1.321183,2.11585,-2.372391,0.4983463),
('id_7e9V82n13',-1.015404,2.451581,0.7866622,-0.8083349,1.044206),
('id_8620Q3376',-1.015404,-0.4780732,-0.4340205,0.5672281,1.583522)

;