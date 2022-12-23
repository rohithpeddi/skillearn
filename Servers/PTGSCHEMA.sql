DROP SCHEMA IF EXISTS PTG_RECIPE_DATA;
CREATE SCHEMA PTG_RECIPE_DATA;

USE PTG_RECIPE_DATA;

DROP TABLE IF EXISTS RECIPE;
CREATE TABLE IF NOT EXISTS RECIPE (
	recipe_id int(11) NOT NULL AUTO_INCREMENT,
    recipe_name varchar(60) NOT NULL,
    PRIMARY KEY (recipe_id),
    Unique(recipe_name)
    ) COMMENT = 'list of all recipes and IDs'
ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS RECIPE_STEP;
CREATE TABLE IF NOT EXISTS RECIPE_STEP (
	recipe_id int(11) NOT NULL,
    step_id int(11) NOT NULL,
    step_name varchar(60) NOT NULL,
    PRIMARY KEY (recipe_id, step_id),
    CONSTRAINT recipe_step_recipe FOREIGN KEY(recipe_id) references recipe(recipe_id)
    ) COMMENT = 'list of all recipes and its steps'
ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS SKILL;
CREATE TABLE IF NOT EXISTS SKILL (
	skill_id int(11) NOT NULL AUTO_INCREMENT,
    skill_name varchar(60) NOT NULL,
    PRIMARY KEY (skill_id),
    Unique(skill_name)
    ) COMMENT = 'list of all skills'
ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS SKILL_NOTES;
CREATE TABLE IF NOT EXISTS SKILL_NOTES (
	recipe_id int(11) NOT NULL,
    step_id int(11) NOT NULL,
    skill_id int(11) NOT NULL,
    skill_level int(11) NOT NULL,
    notes varchar(600),
    PRIMARY KEY (recipe_id, step_id, skill_id, skill_level),
    CONSTRAINT skill_notes_recipe FOREIGN KEY(recipe_id) references recipe(recipe_id),
    CONSTRAINT skill_notes_step FOREIGN KEY(recipe_id, step_id) references recipe_step(recipe_id, step_id),
    CONSTRAINT skill_notes_skill FOREIGN KEY(skill_id) references skill(skill_id)
  ) COMMENT = 'Recipe notes for all skill levels'
ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8;