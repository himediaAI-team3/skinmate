CREATE OR REPLACE VIEW v_recommendation_summary AS
SELECT
    m.member_id,
    si.image_id,
    f.file_url AS skin_image_url,
    d.diagnosis_id,
    d.disease_name,
    d.summary AS diagnosis_summary,
    c.cosmetic_id,
    c.name AS cosmetic_name,
    c.brand AS cosmetic_brand,
    c.price AS cosmetic_price,
    f2.file_url AS cosmetic_image_url,
    r.rationale AS recommendation_reason
FROM recommendation r
JOIN diagnosis d ON r.diagnosis_id = d.diagnosis_id
JOIN skin_image si ON d.image_id = si.image_id
JOIN member m ON si.member_id = m.member_id
JOIN cosmetic c ON r.cosmetic_id = c.cosmetic_id
LEFT JOIN file f ON f.ref_id = si.image_id AND f.ref_type = 'SKIN_IMAGE'
LEFT JOIN file f2 ON f2.ref_id = c.cosmetic_id AND f2.ref_type = 'COSMETIC_IMAGE';