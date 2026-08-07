-- Task #8: seed the problems table with real groep 8 content sourced from
-- docs/content/groep8_math_practice_en.csv. Only the 47 free-response rows
-- (multipulChoice = false) are included - the 17 multiple-choice rows have no
-- home in the current schema/UI yet and stay in the CSV, unseeded, for now.
--
-- correct_answer values are normalized to plain numbers (no "€" or trailing
-- units like " candies") so they parse cleanly through latex_parser.py, which
-- expects math notation, not currency symbols or English words. The original
-- currency/unit context stays in question_text where a student would see it.
insert into problems (topic, difficulty, question_text, correct_answer, solving_tip) values
('calculateInteger', 1, '6 × 199', '1194', '199 is close to 200. First calculate 6 × 200 = 1200, then subtract 6 × 1 = 6. Answer: 1194.'),
('calculateInteger', 1, '4 × 98', '392', '98 is close to 100. Calculate 4 × 100 = 400, then subtract 4 × 2 = 8. Answer: 392.'),
('calculateInteger', 1, '6 × 101', '606', '101 is close to 100. Calculate 6 × 100 = 600, then add 6 × 1 = 6. Answer: 606.'),
('calculateInteger', 2, '4 × 403', '1612', '403 is close to 400. Calculate 4 × 400 = 1600, then add 4 × 3 = 12. Answer: 1612.'),
('calculateInteger', 1, '5 × 99', '495', '99 is close to 100. Calculate 5 × 100 = 500, then subtract 5 × 1 = 5. Answer: 495.'),
('calculateInteger', 2, '7 × 199', '1393', '199 is close to 200. Calculate 7 × 200 = 1400, then subtract 7 × 1 = 7. Answer: 1393.'),
('calculateInteger', 1, '2 × 302', '604', '302 is close to 300. Calculate 2 × 300 = 600, then add 2 × 2 = 4. Answer: 604.'),
('calculateInteger', 1, '4 × 198', '792', '198 is close to 200. Calculate 4 × 200 = 800, then subtract 4 × 2 = 8. Answer: 792.'),
('calculateInteger', 1, '2 × 399', '798', '399 is close to 400. Calculate 2 × 400 = 800, then subtract 2 × 1 = 2. Answer: 798.'),
('calculateInteger', 1, '3 × 202', '606', '202 is close to 200. Calculate 3 × 200 = 600, then add 3 × 2 = 6. Answer: 606.'),
('calculateInteger', 2, '3 × 699', '2097', '699 is close to 700. Calculate 3 × 700 = 2100, then subtract 3 × 1 = 3. Answer: 2097.'),
('calculateInteger', 2, '4 × 802', '3208', '802 is close to 800. Calculate 4 × 800 = 3200, then add 4 × 2 = 8. Answer: 3208.'),
('calculateInteger', 2, '3 × 798', '2394', '798 is close to 800. Calculate 3 × 800 = 2400, then subtract 3 × 2 = 6. Answer: 2394.'),
('calculateInteger', 2, '6 × 999', '5994', '999 is close to 1000. Calculate 6 × 1000 = 6000, then subtract 6 × 1 = 6. Answer: 5994.'),
('calculateInteger', 2, '3 × 701', '2103', '701 is close to 700. Calculate 3 × 700 = 2100, then add 3 × 1 = 3. Answer: 2103.'),
('calculateInteger', 2, '5 × 998', '4990', '998 is close to 1000. Calculate 5 × 1000 = 5000, then subtract 5 × 2 = 10. Answer: 4990.'),
('calculateInteger', 1, '100 × 201', '20100', '201 is close to 200. Calculate 100 × 200 = 20,000, then add 100 × 1 = 100. Answer: 20,100.'),
('calculateInteger', 2, '7 × 399', '2793', '399 is close to 400. Calculate 7 × 400 = 2800, then subtract 7 × 1 = 7. Answer: 2793.'),
('calculateInteger', 3, '101 × 99', '9999', 'Round 99 up to 100: 101 × 100 = 10,100, then subtract 101 × 1 = 101. Answer: 9999.'),
('calculateInteger', 3, '99 × 1001', '99099', '1001 is close to 1000. Calculate 99 × 1000 = 99,000, then add 99 × 1 = 99. Answer: 99,099.'),
('calculateMoney', 1, '2 × €9.50', '19', '€9.50 is close to €10. Calculate 2 × €10 = €20, then subtract 2 × €0.50 = €1. Answer: €19.'),
('calculateMoney', 2, '3 × €19.50', '58.50', '€19.50 is close to €20. Calculate 3 × €20 = €60, then subtract 3 × €0.50 = €1.50. Answer: €58.50.'),
('calculateMoney', 2, '2 × €39.90', '79.80', '€39.90 is close to €40. Calculate 2 × €40 = €80, then subtract 2 × €0.10 = €0.20. Answer: €79.80.'),
('calculateMoney', 2, '4 × €19.50', '78', '€19.50 is close to €20. Calculate 4 × €20 = €80, then subtract 4 × €0.50 = €2. Answer: €78.'),
('calculateMoney', 2, '5 × €19.90', '99.50', '€19.90 is close to €20. Calculate 5 × €20 = €100, then subtract 5 × €0.10 = €0.50. Answer: €99.50.'),
('calculateMoney', 2, '3 × €49.50', '148.50', '€49.50 is close to €50. Calculate 3 × €50 = €150, then subtract 3 × €0.50 = €1.50. Answer: €148.50.'),
('calculateMoney', 2, '4 × €29.90', '119.60', '€29.90 is close to €30. Calculate 4 × €30 = €120, then subtract 4 × €0.10 = €0.40. Answer: €119.60.'),
('calculateMoney', 2, '3 × €39.90', '119.70', '€39.90 is close to €40. Calculate 3 × €40 = €120, then subtract 3 × €0.10 = €0.30. Answer: €119.70.'),
('calculateMoney', 3, '6 × €29.50', '177', '€29.50 is close to €30. Calculate 6 × €30 = €180, then subtract 6 × €0.50 = €3. Answer: €177.'),
('calculateMoney', 2, '4 × €49.50', '198', '€49.50 is close to €50. Calculate 4 × €50 = €200, then subtract 4 × €0.50 = €2. Answer: €198.'),
('calculateMoney', 2, '2 × €69.90', '139.80', '€69.90 is close to €70. Calculate 2 × €70 = €140, then subtract 2 × €0.10 = €0.20. Answer: €139.80.'),
('calculateMoney', 2, '3 × €79.50', '238.50', '€79.50 is close to €80. Calculate 3 × €80 = €240, then subtract 3 × €0.50 = €1.50. Answer: €238.50.'),
('calculateMoney', 2, '3 × €59.90', '179.70', '€59.90 is close to €60. Calculate 3 × €60 = €180, then subtract 3 × €0.10 = €0.30. Answer: €179.70.'),
('calculateMoney', 2, '4 × €79.50', '318', '€79.50 is close to €80. Calculate 4 × €80 = €320, then subtract 4 × €0.50 = €2. Answer: €318.'),
('calculateMoney', 2, '3 × €69.90', '209.70', '€69.90 is close to €70. Calculate 3 × €70 = €210, then subtract 3 × €0.10 = €0.30. Answer: €209.70.'),
('calculateMoney', 3, '8 × €19.50', '156', '€19.50 is close to €20. Calculate 8 × €20 = €160, then subtract 8 × €0.50 = €4. Answer: €156.'),
('calculateMoney', 3, '6 × €19.90', '119.40', '€19.90 is close to €20. Calculate 6 × €20 = €120, then subtract 6 × €0.10 = €0.60. Answer: €119.40.'),
('calculateMoney', 2, '5 × €39.50', '197.50', '€39.50 is close to €40. Calculate 5 × €40 = €200, then subtract 5 × €0.50 = €2.50. Answer: €197.50.'),
('calculateMoney', 3, '8 × €49.90', '399.20', '€49.90 is close to €50. Calculate 8 × €50 = €400, then subtract 8 × €0.10 = €0.80. Answer: €399.20.'),
('calculateMoney', 3, '6 × €89.50', '537', '€89.50 is close to €90. Calculate 6 × €90 = €540, then subtract 6 × €0.50 = €3. Answer: €537.'),
('calculateMoney', 3, '7 × €89.90', '629.30', '€89.90 is close to €90. Calculate 7 × €90 = €630, then subtract 7 × €0.10 = €0.70. Answer: €629.30.'),
('calculateMoney', 3, '7 × €99.50', '696.50', '€99.50 is close to €100. Calculate 7 × €100 = €700, then subtract 7 × €0.50 = €3.50. Answer: €696.50.'),
('calculateMoney', 3, '8 × €79.90', '639.20', '€79.90 is close to €80. Calculate 8 × €80 = €640, then subtract 8 × €0.10 = €0.80. Answer: €639.20.'),
('calculateMoney', 3, '8 × €99.50', '796', '€99.50 is close to €100. Calculate 8 × €100 = €800, then subtract 8 × €0.50 = €4. Answer: €796.'),
('calculateMoney', 3, '9 × €99.90', '899.10', '€99.90 is close to €100. Calculate 9 × €100 = €900, then subtract 9 × €0.10 = €0.90. Answer: €899.10.'),
('calculateInteger', 4, 'Julia has a bag with 37 licorice candies. She shares the candies with 7 friends. Julia and her 7 friends all get the same number of candies. How many candies are left over?', '5', 'Julia plus her 7 friends makes 8 people in total. Divide 37 by 8; the remainder is the answer. Answer: 5 candies.'),
('calculateMoney', 3, 'Anna pays €6 for a bunch of grapes. The bunch weighs 800 grams. How much do the grapes cost per kilogram?', '7.50', 'Convert 800 grams to kilograms (0.8 kg), then divide the price by that weight (€6 ÷ 0.8). Answer: €7.50.');
