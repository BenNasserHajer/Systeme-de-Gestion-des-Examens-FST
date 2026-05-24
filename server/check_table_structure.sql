-- Vérifier la structure de la table compte_enseignant
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'compte_enseignant'
ORDER BY ordinal_position;
