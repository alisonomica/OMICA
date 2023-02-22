USE OMICA;
CREATE TABLE `SAMPLES` (
`SAMPLE_ID` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT ,
`User_id` int unsigned DEFAULT NULL,
`lab_id` int unsigned DEFAULT NULL,
`number_samples` int unsigned NOT NUll DEFAULT '1',
`Freezerworks_location` enum('CDMX','Miami') DEFAULT NULL,
`biosample_type` enum('blood','spittle','nasal swab') DEFAULT NULL,
`panel_desription` varchar(100),
`collection_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Genotypes` (
`Genotype_ID` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT ,
`Sample_ID` int unsigned DEFAULT NULL,
`User_id` int unsigned DEFAULT NULL,
`lab_id` int unsigned DEFAULT NULL,
`sample_kit_id` int unsigned,
`Panel_type` enum('exome', 'genome', 'targeted'),
`Panel_description` varchar(300) default NUll,
`Depth` int UNSIGNED DEFAULT NULL,
`Raw_data_server` enum('omica1','omica2') ,
`Raw_data_folder` varchar(300),
`collection_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
`Secuenced_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Phenotypes-survey_data` (
`Feature_id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT ,
`User_id` int unsigned DEFAULT NULL,
`height` double unsigned DEFAULT NULL ,
`weight` double unsigned DEFAULT NULL,
`smoking_habits` enum ('smoker', 'past_smoker', 'never_smoker', 'unknown'),
`daily_cigarette_cnt` INT unsigned DEFAULT '0' ,
`treatment` ENUM('O2', 'CPAP', 'Intubation', 'unknown'),
`respiratory_frequency` ENUM('low', 'normal', 'high'),
`blood_oxygen_saturation`double unsigned default NULL
);


CREATE TABLE `Phen-Clinical_history` (
`Clinical_ID` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT ,
`User_id` int unsigned DEFAULT NULL,
`record_location` varchar(100) DEFAULT NULL,
`pneumonia` ENUM('absent',' monolateral',' bilateral',' bilatera_diffussed','unknown'),
`Immunocompromised_status`ENUM('TRUE',' FALSE'),
`immunodeficiency`ENUM('option_1',' option_2',' NULL'),
`hematologic_malignancy`ENUM('TRUE',' FALSE'),
`Organ_transplant`ENUM('organ_name',' NULL'),
`asthma`ENUM('TRUE',' FALSE'),
`cystic_fibrosis`ENUM('TRUE',' FALSE'),
`liver_disease`ENUM('disease_name',' NULL'),
`neurological_disease`ENUM('disease_name',' NULL'),
`congestive_heart_failure`ENUM('disease_name',' NULL'),
`kidney_failure`ENUM('TRUE',' FALSE'),
`chronic_obstructive_lung_disease`ENUM('TRUE',' FALSE'),
`cancer`ENUM('disease_name',' NULL')
);
