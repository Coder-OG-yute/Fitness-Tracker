# NEA Completed Sections – Eothain Fernades
# All text below is NEW writing (highlight RED in your Word document)
# Each section is clearly labelled — copy and paste it into the matching place in your doc.
# Where [INSERT DIAGRAM] appears, you need to add that diagram yourself (e.g. in draw.io).

---

## ⚠️ CLEAN-UP NOTES FOR EXISTING SECTIONS BEFORE SUBMITTING

Before copying in the new sections, remove these placeholder notes from your document:

- **1.3.2**: Remove "*use ai" and "Flourish studio diagram e then take away from info of diagram" — replace with the actual Flourish diagram and your written analysis of it (which you said you had — just insert it properly)
- **1.3.3**: Remove "Include flow diagrams of current systems AJ" from the top — insert the actual flowcharts there
- **1.4.1**: Remove the "*modify text" note
- **1.4.3**: Remove "Having began my research and solidified my idea, I consulted my proposal form and updated" — the full 1.4.3 text below replaces this
- **4. Testing**: Remove the markscheme pasted under the section heading — your testing section should start with the intro paragraph and table below
- **5. Evaluation**: Remove the markscheme pasted under the section heading — replace with the evaluation text below

---

## SECTION 1.3.5 – Problem Statement

Based on my client interview, my survey of 20 fitness-interested individuals, and my analysis of existing systems like freeworkoutlog, the problem is clear: there is no accessible, all-in-one fitness and diet tracking platform that genuinely meets the needs of the average person trying to make real, visible progress.

My client had previously tried tracking her progress but found existing systems demotivating and ultimately not worth the effort — not providing meaningful feedback, separating diet and exercise tracking across different tools, and failing to make progress feel tangible. This wasn't an isolated experience; 18 out of 20 of those I surveyed do not currently track their progress, and all 20 said they felt current fitness trackers didn't provide any real help. The analysis of freeworkoutlog confirmed this pattern — whilst it allows exercise logging, it separates diet tracking entirely, lacks scientific guidance, offers only a weekly diary view with limited graph options, and is confusing to navigate. These are all pain points that my research directly identified.

The core problem is therefore not a shortage of fitness tracking tools, but a shortage of tools that are actually effective, engaging and consolidated enough to be worth using consistently. Users want visual progress tracking, structured guidance grounded in science, and a single platform that handles both exercise and diet — not a fragmented, number-heavy experience that feels like a chore. My solution is designed to address exactly this gap.

---

## SECTION 1.4.1 – Initial Project Plan

The target audience for my program is primarily my mother as the direct client, but extends to any person interested in fitness and diet tracking — a demographic that is only growing as health and body transformation become a more prominent part of everyday life. The program is designed with the regular, non-expert user in mind, making it accessible to anyone trying to improve their health and not just experienced fitness enthusiasts.

The solution is a web-based fitness and diet tracker built using Python (Flask) on the backend, HTML and CSS on the frontend, and a SQLite relational database to store all user data. The program operates in a calendar-based format through which users can log and review their progress over time. The core features planned and implemented are:

- Exercise logging, covering both strength training (capturing exercise, sets, reps and weight lifted) and cardio (capturing exercise type and duration), with calories burnt estimated automatically from MET values and the user's body weight
- Diet and food logging using a food database, where users can search any food by name, specify the amount in grams, and have the relevant macros (calories and protein) calculated and saved automatically
- Progress analytics and graphs providing visual representations of weight history, strength progression per exercise, protein intake, and calorie balance — all viewable across daily, weekly, monthly and yearly time periods
- A goals system allowing users to set personal targets (e.g. bench press 100 kg by a target date) and track their progress as a percentage towards each
- A tips and advice page featuring science-backed guidance on exercise and diet, searchable by keyword and filterable by category
- Workout presets, allowing users to save a set of exercises as a named workout they can quickly reuse and log in full

The technical skills this project involves include relational database design and management with SQL, web-based programming with Python (Flask), HTML and CSS, object-oriented programming through class-based models (Goal, WorkoutPreset, ExercisePreset), use of a third-party API (FatSecret) for food nutrition data, and custom algorithm and data structure implementation including a binary search function and Stack and Queue data structures.

---

## SECTION 1.4.2 – Solution to the Problem

The solution is a web application built with Python (Flask) on the backend and HTML/CSS on the frontend, using a SQLite relational database to store all user data. It tackles the core problem identified through my research — the absence of a consolidated, engaging and genuinely useful fitness and diet tracking platform — by bringing all the features users need into one accessible system.

A central part of the solution is a food logging system powered by the FatSecret API, which the user can search by food name and a mass in grams. The system retrieves the corresponding macros — calories and protein — and logs them against the user's account and the relevant date. This removes the burden of manual calorie calculation from the user and makes nutritional tracking both accurate and easy, regardless of the user's knowledge of nutrition.

For exercise, users log sessions as either gym-based — specifying the exercise, sets, reps and weight — or cardio — specifying exercise type and duration. Calories burnt are estimated automatically from each exercise's MET value and the user's logged body weight, using the formula: MET × weight (kg) × time (hours). For gym exercises, time is estimated from sets and reps rather than requiring the user to input it, since most users wouldn't know this. This is a significant improvement over systems like freeworkoutlog, which required users to manually enter calories burnt — information most users simply don't have.

Progress is made visible through a dedicated analytics page that generates graphs of weight history, strength progression per exercise, daily protein intake, and a calorie balance comparison between calories consumed and calories burnt — all filterable by daily, weekly, monthly or yearly time periods. This directly addresses the most demanded feature from my research, where 18 of 20 interviewees wanted visual representation of their progress.

A tips page provides science-backed guidance on both diet and exercise, searchable by keyword and filterable by category, so users can access relevant information to help them understand their training and nutrition. This bridges the knowledge gap identified in my research, where the majority of users said they weren't particularly informed on the science behind exercise and diet — meaning a tool that both tracks and educates is far more useful than a passive logger alone.

---

## SECTION 1.4.3 – Features and Function

Having begun my research and solidified my idea, I finalised the core features of my solution based on the user requirements identified and updated my initial project plan accordingly.

### 1.4.3.1 Feature 1 – Tips and Advice System

One of the most consistent findings from my research was that users don't just want to log numbers — they want guidance and context. 4 of the 20 interviewees specifically named structured guidance as a valued feature, and the majority stated they were not informed on the science of exercise or diet. My client expressed the same frustration — she wanted to understand why she had plateaued and what adjustments in technique and diet would actually make a difference, not just a log of what she'd done.

To address this, I built a tips and advice page where science-backed guidance on both exercise and diet is stored in the database and served to the user. Each tip has a title, full content, a category (exercise or diet) and a cited source. The page allows users to load a random tip, browse all tips by category, or search by keyword — so they can find guidance relevant to whatever they're currently focused on. Exercise tips include guidance on progressive overload, the importance of emphasising the eccentric phase of a lift for muscle hypertrophy, rest and recovery, and warming up correctly. Diet tips cover protein targets (1.6–2.2 g per kg of body weight for muscle building), hydration, whole food nutrition and supplement information — including creatine dosing and its evidence-based benefits.

This transforms the program from a passive logging tool into an active guidance resource, which was a clear gap in existing systems — freeworkoutlog, for example, had a list of exercises with basic instructions but no broader tips on exercise science or nutrition at all.

The search functionality uses SQL LIKE queries and processes the results through a Queue data structure — first in, first out — to maintain the correct order of tips returned, providing a practical implementation of a custom data structure as part of the system's functionality.

### 1.4.3.2 Feature 2 – Progress Analytics and Graphs

Visual progress representation was the single most requested feature in my survey — 18 of 20 interviewees said charts and diagrams would make their progress more tangible and help keep them motivated, particularly through periods where they felt they had plateaued and the scale wasn't moving. My client specifically said that numbers alone don't mean much to her, but being able to see changes clearly over time — even small ones — would keep her engaged. This fed directly into one of the most important features of my solution.

The analytics page generates several charts dynamically from the user's own logged data:

- **Weight history graph** — plots the user's logged body weight over time, showing trends in fat loss or weight gain across a selectable time period
- **Strength progression chart** — tracks a selected exercise over time, plotting weight-per-rep for gym exercises or duration for cardio, so users can see clearly whether they're getting stronger or fitter
- **Calorie balance graph** — compares total calories consumed (from diet logs) against total calories burnt (from exercise logs) to show the net calorie surplus or deficit per period
- **Protein intake graph** — tracks daily or weekly protein intake from diet logs, allowing the user to see consistency against their target

All four charts support four time views — daily, weekly, monthly and yearly — switchable using buttons on the analytics page, so users can zoom in on recent sessions or step back and see long-term progress. The data for each chart is served from a dedicated JSON API endpoint and rendered on the frontend. This is a significant improvement over freeworkoutlog, which only showed a weekly diary view with no calorie or nutrition graphs at all.

### 1.4.3.3 Feature 3 – Food and Exercise Database

For the program to be genuinely useful to the average person, it needs to remove the guesswork. The food database, powered by the FatSecret API, allows users to search for any food by name, specify the amount in grams, and have the calories and protein automatically calculated and logged to their account. Users don't need to read nutritional labels or manually look up macro information — the system does it for them — making diet tracking both accurate and accessible regardless of the user's nutritional knowledge.

For exercise, a built-in exercise library categorises all available exercises by type — gym or cardio — and stores a MET (Metabolic Equivalent of Task) value for each. When logging, the available exercises are dynamically filtered based on the selected type, so only gym exercises appear when gym is selected and only cardio exercises appear for cardio, preventing incorrect or mixed entries. The system then uses the MET value alongside the user's most recently logged body weight to estimate calories burnt using the formula: MET × weight (kg) × time (hours). A custom binary search algorithm is applied to the alphabetically sorted exercise list to efficiently locate the chosen exercise and retrieve its MET value.

All inputs are validated server-side to maintain data integrity: weight must be at least 0.1 kg, sets and reps must be at least 1, cardio duration must be at least 1 minute, and dates must fall within a valid range (1900–2200). If any input fails validation, an appropriate error message is displayed and the form is re-rendered so the user can correct the entry before it is saved. This ensures only accurate and meaningful data is stored, maintaining the integrity of the user's progress records throughout.

---

## SECTION 1.5 – Possible Limitations

No system is without limitations, and it's important to acknowledge both the broader structural constraints and the more specific functional ones that apply to this project.

On a macro level, the program is only accessible via a hosted link in a browser — it is not a downloadable application and is not available on any app store, meaning it requires an internet connection to run and is not as immediately accessible as a commercial mobile app. The SQLite database used is well-suited for a single-user or small-scale deployment but is not designed for high concurrency; scaling the system to a large number of simultaneous users would require migrating to a more capable database system, such as PostgreSQL, which is beyond the scope of this project.

On a micro level, the exercise library covers a broad range of common gym and cardio exercises but is not exhaustive — users may encounter exercises not in the preset list. Unlike freeworkoutlog, my system does not currently support fully custom exercise entries, which was something I had initially planned to include but was not implemented in the final version. Similarly, the food logging feature relies entirely on the FatSecret API — if the API returns no result for a given food name, the food cannot be logged, which means the system is dependent on the coverage and accuracy of a third-party data source.

The calorie-burn calculations for both cardio and gym exercises are estimates derived from standard MET values and the user's most recently logged body weight. They are not personalised to individual fitness levels, heart rate or metabolic rate and should be understood as approximations rather than precise measurements. This is an inherent limitation of MET-based calorie estimation and is a point I acknowledge in the tips section of the program.

---

## SECTION 1.6 – Data Dictionary

The following data dictionary describes the structure of each table in the SQLite relational database used by the system. All tables are created on startup if they do not already exist.

---

**Table: users**
| Field Name    | Data Type | Size / Constraint          | Description                                      |
|---------------|-----------|----------------------------|--------------------------------------------------|
| userId        | INTEGER   | PRIMARY KEY AUTOINCREMENT  | Unique identifier for each user                  |
| username      | TEXT      | UNIQUE, NOT NULL           | User's chosen username for login                 |
| email         | TEXT      | UNIQUE, NOT NULL           | User's email address                             |
| passwordHash  | TEXT      | NOT NULL                   | Hashed password (pbkdf2:sha256 via Werkzeug)     |
| createdAt     | TEXT      |                            | Date and time the account was created            |

---

**Table: exercises**
| Field Name    | Data Type | Size / Constraint          | Description                                          |
|---------------|-----------|----------------------------|------------------------------------------------------|
| exerciseId    | INTEGER   | PRIMARY KEY AUTOINCREMENT  | Unique identifier for each exercise                  |
| exerciseName  | TEXT      | UNIQUE, NOT NULL           | Name of the exercise (e.g. "Bench press")            |
| exerciseType  | TEXT      |                            | Type: 'gym' or 'cardio'                              |
| metValue      | REAL      |                            | MET value used for calorie estimation                |

---

**Table: exerciseLogs**
| Field Name     | Data Type | Size / Constraint                          | Description                                         |
|----------------|-----------|--------------------------------------------|-----------------------------------------------------|
| logId          | INTEGER   | PRIMARY KEY AUTOINCREMENT                  | Unique identifier for each log entry                |
| userId         | INTEGER   | FOREIGN KEY → users(userId)                | ID of the user who logged this exercise             |
| exerciseId     | INTEGER   | FOREIGN KEY → exercises(exerciseId)        | ID of the exercise performed                        |
| date           | TEXT      |                                            | Date of the exercise session (YYYY-MM-DD)           |
| sets           | INTEGER   |                                            | Number of sets completed (gym only)                 |
| reps           | INTEGER   |                                            | Number of reps per set (gym only)                   |
| weight         | REAL      |                                            | Weight lifted in kg (gym only)                      |
| duration       | REAL      |                                            | Duration in minutes (cardio only)                   |
| caloriesBurned | REAL      |                                            | Estimated calories burnt, calculated from MET       |

---

**Table: dietLogs**
| Field Name | Data Type | Size / Constraint               | Description                                         |
|------------|-----------|---------------------------------|-----------------------------------------------------|
| logId      | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for each diet log entry           |
| userId     | INTEGER   | FOREIGN KEY → users(userId)     | ID of the user who logged this food item            |
| foodName   | TEXT      |                                 | Name of the food as returned by the FatSecret API   |
| date       | TEXT      |                                 | Date the food was eaten (YYYY-MM-DD)                |
| mass       | REAL      |                                 | Mass of food consumed in grams                      |
| calories   | REAL      |                                 | Calories in the logged amount, from the API         |
| protein    | REAL      |                                 | Protein in grams in the logged amount, from API     |

---

**Table: workoutPresets**
| Field Name    | Data Type | Size / Constraint               | Description                                                        |
|---------------|-----------|---------------------------------|--------------------------------------------------------------------|
| id            | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for the preset                                   |
| userId        | INTEGER   | FOREIGN KEY → users(userId)     | ID of the user who created the preset                              |
| presetName    | TEXT      |                                 | Name of the workout preset (e.g. "Push Day")                       |
| exercisesJson | TEXT      |                                 | JSON-serialised list of exercises stored in the preset             |
| createdAt     | TEXT      |                                 | Date and time the preset was created                               |
| updatedAt     | TEXT      |                                 | Date and time the preset was last modified                         |

---

**Table: goals**
| Field Name   | Data Type | Size / Constraint               | Description                                              |
|--------------|-----------|---------------------------------|----------------------------------------------------------|
| id           | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for the goal                           |
| userId       | INTEGER   | FOREIGN KEY → users(userId)     | ID of the user who set this goal                         |
| goalType     | TEXT      |                                 | Category of goal (e.g. 'strength', 'weight', 'protein')  |
| targetValue  | REAL      |                                 | The target value to reach (e.g. 100 kg bench press)      |
| targetDate   | TEXT      |                                 | Target date to achieve the goal by                       |
| currentValue | REAL      |                                 | Most recently logged current value for this goal         |
| unit         | TEXT      |                                 | Unit for the goal (e.g. 'kg', 'g')                       |
| description  | TEXT      |                                 | User-written description of the goal                     |
| createdAt    | TEXT      |                                 | Date and time the goal was created                       |

---

**Table: bodyWeight**
| Field Name | Data Type | Size / Constraint               | Description                                         |
|------------|-----------|---------------------------------|-----------------------------------------------------|
| id         | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for the weight log entry          |
| userId     | INTEGER   | FOREIGN KEY → users(userId)     | ID of the user who logged this weight               |
| weight     | REAL      |                                 | Body weight in kg                                   |
| date       | TEXT      |                                 | Date of the weight log (YYYY-MM-DD)                 |
| createdAt  | TEXT      |                                 | Date and time the entry was created                 |

---

**Table: nutritionDatabase**
| Field Name       | Data Type | Size / Constraint         | Description                                        |
|------------------|-----------|---------------------------|----------------------------------------------------|
| id               | INTEGER   | PRIMARY KEY AUTOINCREMENT | Unique identifier for the entry                    |
| foodName         | TEXT      | UNIQUE                    | Name of the food item                              |
| caloriesPer100g  | REAL      |                           | Calories per 100 g of this food                    |
| proteinPer100g   | REAL      |                           | Protein (g) per 100 g of this food                 |
| carbsPer100g     | REAL      |                           | Carbohydrates (g) per 100 g of this food           |
| fatsPer100g      | REAL      |                           | Fats (g) per 100 g of this food                    |

---

**Table: tips**
| Field Name | Data Type | Size / Constraint         | Description                                              |
|------------|-----------|---------------------------|----------------------------------------------------------|
| id         | INTEGER   | PRIMARY KEY AUTOINCREMENT | Unique identifier for the tip                            |
| category   | TEXT      |                           | Category of the tip: 'exercise' or 'diet'                |
| title      | TEXT      |                           | Short title of the tip (e.g. "Progressive Overload")     |
| content    | TEXT      |                           | Full text of the tip                                     |
| source     | TEXT      |                           | Source or reference cited for the tip                    |

---

## SECTION 2 – Documented Design

*(All diagram placeholders below need to be drawn in draw.io or similar and inserted — the text descriptions are written for you)*

### 2.1 High-Level System Overview

The solution is a web application following a client-server architecture. The frontend — built in HTML and CSS — runs in the user's browser and communicates with the backend via HTTP requests. The backend is a Flask application written in Python, which handles all business logic, data processing and database interaction. Data is stored persistently in a SQLite relational database. A third-party API (FatSecret) is called at the time of food logging to retrieve macro-nutrient data for the food item and mass entered by the user.

The Flask application is structured using Blueprints, which organise the routes into logical modules by function: authentication (auth), dashboard and weight logging (dashboard), exercise logging and presets (exercise), diet logging (diet), analytics and graphs (analytics), goals (goals) and tips (tips). Each Blueprint handles the routes, GET/POST request logic and database interaction for its respective area of the system.

[INSERT SYSTEM FLOWCHART HERE — show: browser → Flask app → SQLite DB, and the API call to FatSecret from the diet route]

### 2.2 Database Design

The database consists of eight interrelated tables. The central table is users, which every other data table references via a foreign key on userId — ensuring all logged data is associated with a specific user account. The exerciseLogs table references both users and exercises via foreign keys, forming a many-to-one relationship: one user can have many exercise log entries, and each entry links to one exercise from the exercises table. The dietLogs, workoutPresets, goals and bodyWeight tables all follow the same pattern — each has a foreign key to users, associating all personal data with the account.

The exercises table is a shared reference table — it is not user-specific and stores the predefined list of exercises with their MET values, populated on database creation. The tips table is similarly static, storing science-backed tips that are read by all users.

[INSERT E-R DIAGRAM HERE — show: users at the centre with one-to-many relationships to exerciseLogs, dietLogs, workoutPresets, goals, bodyWeight; exerciseLogs also linked to exercises; exercises and tips as independent/reference tables]

### 2.3 Key Algorithm Descriptions

#### 2.3.1 Binary Search (Exercise Lookup)

When a user submits the exercise log form, the exercise name they selected must be matched to a record in the exercises database table to retrieve its MET value. Rather than use a basic SQL lookup directly, I implemented a binary search algorithm on a pre-fetched alphabetically sorted list of exercise names. The function `binSearch(sortedNameList, targetName)` operates as follows:

```
SET lowIndex = 0
SET highIndex = length of list - 1

WHILE lowIndex <= highIndex:
    SET midIndex = (lowIndex + highIndex) // 2
    IF list[midIndex] == targetName (case-insensitive):
        RETURN midIndex         ← found
    ELSE IF targetName < list[midIndex]:
        SET highIndex = midIndex - 1    ← search left half
    ELSE:
        SET lowIndex = midIndex + 1     ← search right half

RETURN -1   ← not found
```

Binary search has a time complexity of O(log n), making it significantly more efficient than a linear search — especially as the exercise list grows. If the function returns -1, an error is flashed to the user and the entry is not saved. The corresponding exerciseId is then retrieved from a parallel `idList` at the matched index.

#### 2.3.2 Calorie Estimation Algorithm (MET Formula)

The calories burnt for any logged exercise are estimated using the Metabolic Equivalent of Task (MET) formula:

**Calories = MET × body weight (kg) × time (hours)**

For cardio exercises, time is derived directly from the user's logged duration in minutes (converted to hours). For gym exercises, since the user logs sets and reps rather than duration, time is estimated using the formula:

**Estimated time (seconds) = (sets × reps × 3) + (sets × 60)**

This assumes approximately 3 seconds per rep and 60 seconds of rest per set — a reasonable average for strength training. The user's most recently logged body weight is retrieved from the bodyWeight table; if no weight has been logged, a default of 70 kg is used. The result is rounded to one decimal place and stored in the exerciseLogs table.

#### 2.3.3 Password Hashing (User Authentication)

Passwords are never stored in plain text. On registration, the password entered is hashed using the `pbkdf2:sha256` method via the Werkzeug `generate_password_hash` function. This applies a salted hash, meaning even if two users set the same password, the stored hashes will differ. On login, the entered password is compared against the stored hash using `check_password_hash`, which returns a boolean. If it returns False, the login is rejected and an error is displayed — the user is never told which of the username or password was incorrect, to prevent enumeration.

Before hashing, the password is validated using a custom `valPass` function that checks: minimum length of 8 characters, presence of at least one uppercase letter, one lowercase letter, one digit, and one special character. Any failures are returned as a list of error messages and flashed to the user on the sign-up form.

#### 2.3.4 Goal Progress Calculation

The `Goal` class includes a `calcProgress()` method that calculates the user's progress towards a goal as a percentage:

```
IF targetValue == 0:
    RETURN 0
ELSE:
    percentage = (currentValue / targetValue) × 100
    RETURN ROUND(percentage, 1)
```

This is capped at 100% on the frontend. The current value is manually updated by the user via the goals page, and the resulting progress percentage is passed as JSON to the analytics page to render a bar chart of all active goals.

#### 2.3.5 FatSecret API Call – Macro-Nutrient Retrieval for Diet Logging

When a user submits the diet log form, the program needs to find the calories and protein for the food they entered and the mass in grams they specified. Because there is no practical way to store every food in existence in a local database, this is handled by calling the FatSecret API — an external web service that holds a large food nutrition database. The algorithm in `fatsecret_api.py` (`getFoodMacro`) works as follows:

```
RECEIVE foodName (text entered by user), mass (grams entered by user)

STEP 1 – Search for the food:
    results = FatSecret.foods_search(foodName)
    IF results is empty:
        RETURN None  ← no match found, caller will show error

STEP 2 – Take the first result:
    firstItem = results[0]
    foodName  = firstItem["food_name"]
    foodID    = firstItem["food_id"]

STEP 3 – Get full nutritional detail for that food:
    detailFood = FatSecret.food_get(foodID)
    servings   = detailFood["servings"]["serving"]

    IF servings is a single dict (not a list):
        serving = servings           ← normalise: use it directly
    ELSE:
        serving = servings[0]        ← take first serving from the list

STEP 4 – Extract raw values from the serving:
    caloriesPerServing = float(serving["calories"])
    proteinPerServing  = float(serving["protein"])
    servingMass        = float(serving["metric_serving_amount"])

    IF servingMass == 0:
        RETURN None   ← cannot divide by zero

STEP 5 – Scale to the mass the user entered:
    perGram        = 1 / servingMass
    totalCalories  = ROUND(caloriesPerServing × perGram × mass, 1)
    totalProtein   = ROUND(proteinPerServing  × perGram × mass, 1)

RETURN { foodName, totalCalories, totalProtein }
```

The result is then passed back to `calcNutrients` in `nutrition.py`, which additionally caches the per-100g values into the local `nutritionDatabase` table using `INSERT OR IGNORE` — so foods looked up before do not require a repeat API call if referenced later. The final calories and protein values are inserted into the `dietLogs` table and shown to the user in a success message.

The key challenge this algorithm solves is that FatSecret does not return values per 100 g directly — it returns values per serving, where each food's serving size varies. The `perGram` calculation (1 ÷ servingMass) converts this to a per-gram rate, which is then scaled by whatever mass the user entered, making the result accurate regardless of how much of the food was eaten.

#### 2.3.6 Analytics Data Aggregation and Graph Rendering

The analytics page displays four charts — weight history, strength progression, calorie balance, and protein intake — all of which support four selectable time views: daily, weekly, monthly, and yearly. Each chart is driven by a separate JSON API endpoint on the backend, and rendered on the frontend by a charting library using the data returned. The algorithm below describes how the data aggregation works for each time period, using the calorie balance chart as the example since it is the most complex (it queries two tables and computes a net value):

```
RECEIVE period (from user button click: "daily" / "weekly" / "monthly" / "yearly")

STEP 1 – Query calories SPENT (from exercise logs):
    IF period == "daily":
        SQL: SELECT date, SUM(caloriesBurned)
             FROM exerciseLogs WHERE userId = ?
             GROUP BY date

    IF period == "weekly":
        SQL: SELECT date(date, 'weekday 0', '-6 days') as week_start,
                    SUM(caloriesBurned)
             FROM exerciseLogs WHERE userId = ?
             GROUP BY strftime('%Y-%W', date)

    IF period == "monthly":
        SQL: SELECT strftime('%Y-%m', date), SUM(caloriesBurned)
             FROM exerciseLogs WHERE userId = ?
             GROUP BY strftime('%Y-%m', date)

    IF period == "yearly":
        SQL: SELECT strftime('%Y', date), SUM(caloriesBurned)
             FROM exerciseLogs WHERE userId = ?
             GROUP BY strftime('%Y', date)

    → Store result as dict: spent_by = { period_label: calories_burned }

STEP 2 – Query calories GAINED (from diet logs):
    Same structure as Step 1 but queries dietLogs and SUM(calories)
    → Store result as dict: gained_by = { period_label: calories_eaten }

STEP 3 – Merge both sets of period labels:
    all_periods = SORT( UNION of keys in spent_by and gained_by )
    (so periods where only exercise OR only diet was logged still appear)

STEP 4 – Build the data list:
    FOR each period_label in all_periods:
        spent  = spent_by.get(period_label, 0)    ← default 0 if no exercise that period
        gained = gained_by.get(period_label, 0)   ← default 0 if no food logged that period
        net    = gained - spent
        APPEND { period: period_label, spent: spent, gained: gained, net: net }

STEP 5 – Return as JSON:
    RETURN jsonify(dataList)
```

For the strength progression chart, an additional aggregation step — `periodKey()` — is applied in Python after the SQL query rather than in SQL itself, since the data must first be split by exercise name before being grouped by time period:

```
FOR each data point in a given exercise's history:
    label = periodKey(date, period)
        → daily:   label = "YYYY-MM-DD"
        → weekly:  label = week start date (subtract days since Sunday)
        → monthly: label = "YYYY-MM"
        → yearly:  label = "YYYY"

    ADD y_value to bucket[label]
    INCREMENT count in bucket[label]

FOR each bucket:
    averaged_y = y_sum / count   ← average value across all sessions in that period
    APPEND { date: label, yValue: averaged_y }

SORT buckets by sort_key (chronological order)
```

For gym exercises, the y-value plotted is **weight ÷ total reps** (weight per rep), which gives a single number that rises as the user gets stronger regardless of how many sets they do. For cardio exercises, the y-value is simply the **duration in minutes**. This makes strength progression directly comparable across sessions even when the user varies their sets or reps.

On the frontend, once the JSON is received from the endpoint, the charting library reads the array of `{ date, value }` objects and plots each as a data point on a line or bar chart. The user can switch time periods using the Daily / Weekly / Monthly / Yearly buttons, which trigger a new fetch request to the same endpoint with a different `?period=` query parameter, and the chart re-renders with the newly aggregated data.

### 2.4 Data Structures

Two custom data structures are implemented in `data_structures.py` and used actively in the system:

**Stack (LIFO):** Used in workout presets to manage the list of exercises within a preset. Exercises are pushed onto the stack when added and can be removed at a specific index using `remove_at(index)`. The Stack class wraps a Python list and provides `push`, `pop`, `is_empty`, `__len__` and `__iter__` operations, meaning it can be iterated over when serialising the preset to JSON for database storage.

**Queue (FIFO):** Used in the tips search functionality. When search results are returned from the database, they are enqueued into a Queue one at a time and dequeued in order to build the final list returned as JSON. This maintains the order in which tips are returned — first result in is first result out — and serves as a real implementation of the Queue data structure within the system.

### 2.5 User Interface Design

The user interface is built with HTML and CSS across the following pages:

- **Login / Sign-up** — entry point for the application; sign-up validates username, email, password and confirm password fields before creating an account
- **Dashboard** — landing page after login; provides navigation links to all sections of the app
- **Exercise Log** — form for logging a single exercise session or applying a workout preset; exercise type selection (gym/cardio) dynamically filters the exercise list
- **Workouts** — page for creating and managing named workout presets; exercises can be added, removed and viewed per preset
- **Diet Log** — form for searching and logging a food item by name and mass in grams
- **Calendar** — monthly calendar view showing all exercise and diet logs by date; togglable between exercise and diet views with edit/delete options per entry
- **Analytics** — graphs page showing weight history, strength progression, calorie balance and protein intake, each with daily/weekly/monthly/yearly view buttons
- **Goals** — page to create, view, edit, update progress on and delete personal fitness goals; progress shown as a percentage bar chart
- **Tips** — advice page with random tip loader, category filter buttons (exercise/diet) and keyword search
- **Weight Log** — form to log body weight with date; shows paginated history of past entries with edit/delete options

[INSERT WIREFRAMES / SCREENSHOTS OF KEY PAGES HERE — e.g. the dashboard, the exercise log form, the analytics page, the calendar]

---

## SECTION 3 – Implementation / Technical Solution (Overview Guide)

*(This section is primarily your annotated code. The text below is an overview guide to put at the start of Section 3 before your code listing. You should then paste your code in sections as described.)*

### Overview Guide

The solution is a Flask-based web application written in Python, using a SQLite database and HTML/CSS frontend. To run the solution, navigate to the `Fitness Tracker/` directory and run `python main.py` — the application will start on `http://127.0.0.1:5000`. The database (`database/fitness_tracker.db`) is created and populated with default data (exercises, tips) automatically on first run.

The project is structured as follows:

| File / Folder                  | Purpose                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| `main.py`                     | Entry point; registers blueprints and opens/closes the database        |
| `app/__init__.py`             | Flask app factory                                                       |
| `app/routes/auth.py`          | Sign-up, login, logout routes (user authentication)                    |
| `app/routes/dashboard.py`     | Dashboard, calendar, and weight logging routes                         |
| `app/routes/exercise.py`      | Exercise log, workout presets and related routes                       |
| `app/routes/diet.py`          | Food/diet log routes and FatSecret API calls                           |
| `app/routes/analytics.py`     | JSON endpoints for all analytics chart data                            |
| `app/routes/goals.py`         | Goal creation, editing, progress update and deletion routes            |
| `app/routes/tips.py`          | Tips page, random tip, search and category filter routes               |
| `app/models/goal.py`          | Goal class with `saveToDB`, `loadGoals`, `calcProgress` methods        |
| `app/models/preset.py`        | WorkoutPreset, ExercisePreset and PresetInstance classes               |
| `app/utils/db.py`             | Database connection, table creation, default data insertion            |
| `app/utils/search.py`         | Binary search algorithm (`binSearch`)                                  |
| `app/utils/data_structures.py`| Custom Stack (LIFO) and Queue (FIFO) implementations                  |
| `app/utils/password.py`       | Password validation function (`valPass`)                               |
| `app/utils/nutrition.py`      | Nutrient calculation wrapper                                           |
| `app/utils/fatsecret_api.py`  | FatSecret API integration for food macro retrieval                     |
| `app/templates/`              | HTML templates for all pages                                           |
| `database/fitness_tracker.db` | SQLite database file                                                   |

The most technically complex parts of the solution are:
- The binary search implementation in `utils/search.py`, used for exercise lookup during logging
- The Stack and Queue data structures in `utils/data_structures.py`, used in workout presets and tips search respectively
- The MET-based calorie estimation in `routes/exercise.py`
- The multi-table SQL queries in `routes/analytics.py` and `routes/dashboard.py`, including GROUP BY aggregation and cross-table JOINs
- The OOP model in `models/goal.py` and `models/preset.py`, where objects are dynamically created from database rows
- The password hashing and validation in `routes/auth.py` and `utils/password.py`

*(Paste your code sections after this guide, broken into clearly labelled parts — e.g. "Authentication", "Exercise Logging", "Analytics", etc. Paste the SQL table creation from db.py separately and label it "Database Schema")*

---

## SECTION 4 – Testing

### Testing Introduction

Testing was carried out through a video walkthrough of the completed system, capturing a representative sample of tests across the core requirements. Each test is documented in the table below with a corresponding video timestamp so the assessor can locate the evidence for each test. The video is available at: [INSERT VIDEO URL HERE — upload to YouTube or Google Drive and paste the link]

The tests cover: user authentication, exercise logging (both gym and cardio), diet logging, validation of inputs, progress graph generation, the tips system, the goals system and workout presets. Test types used are: Normal (valid input, expected to succeed), Boundary (edge case values), and Erroneous (invalid input, expected to be rejected).

---

### Test Table Template

Copy this table into your document and fill in the Actual Outcome and Timestamp columns as you record your video.

| Test No. | Feature / Section          | Test Description                                                        | Test Type  | Test Data                                                 | Expected Outcome                                               | Actual Outcome | Timestamp | Pass/Fail |
|----------|---------------------------|-------------------------------------------------------------------------|------------|-----------------------------------------------------------|----------------------------------------------------------------|----------------|-----------|-----------|
| 1        | Sign-up                    | Register a new account with valid details                               | Normal     | Username: testuser, Email: test@test.com, Password: Test123! | Account created, redirected to login, success message shown    |                |           |           |
| 2        | Sign-up validation         | Attempt to register with passwords that don't match                     | Erroneous  | Password: Test123! / Confirm: Test456!                     | Error message: "Passwords do not match"                        |                |           |           |
| 3        | Sign-up validation         | Attempt to register with a weak password (no uppercase/symbol)          | Erroneous  | Password: simplepassword1                                  | Error message listing missing requirements                     |                |           |           |
| 4        | Sign-up validation         | Attempt to register with an already-taken username                      | Erroneous  | Username already in database                               | Error message: "Username or email already exists"              |                |           |           |
| 5        | Login                      | Login with correct credentials                                          | Normal     | Valid username and password                                | Redirected to dashboard, success message shown                 |                |           |           |
| 6        | Login validation           | Login with incorrect password                                           | Erroneous  | Correct username, wrong password                           | Error message: "Invalid username or password"                  |                |           |           |
| 7        | Exercise log – gym         | Log a gym exercise with valid sets, reps and weight                     | Normal     | Exercise: Bench press, Sets: 3, Reps: 10, Weight: 60 kg, Date: valid | Exercise logged, calorie estimate shown in success message |                |           |           |
| 8        | Exercise log – gym validation | Attempt to log gym exercise with reps = 0                             | Erroneous  | Sets: 3, Reps: 0, Weight: 60 kg                           | Error message: "Sets and reps must be at least 1"              |                |           |           |
| 9        | Exercise log – gym validation | Attempt to log gym exercise with text in weight field                 | Erroneous  | Weight: "heavy"                                            | Error message: "Invalid number format"                         |                |           |           |
| 10       | Exercise log – cardio      | Log a cardio exercise with valid duration                               | Normal     | Exercise: Running (10 km/h), Duration: 30 min, Date: valid | Exercise logged, calorie estimate shown in success message     |                |           |           |
| 11       | Exercise log – cardio validation | Attempt to log cardio with duration < 1 minute                   | Boundary   | Duration: 0.5                                              | Error message: "Duration must be at least 1 minute"            |                |           |           |
| 12       | Exercise log – type filter | Select "Gym" exercise type and verify only gym exercises appear         | Normal     | Exercise type: Gym                                         | Dropdown/list shows only gym exercises, no cardio options      |                |           |           |
| 13       | Exercise log – type filter | Select "Cardio" exercise type and verify only cardio exercises appear   | Normal     | Exercise type: Cardio                                      | Dropdown/list shows only cardio exercises, no gym options      |                |           |           |
| 14       | Diet log                   | Log a food item with valid name and mass                                | Normal     | Food: chicken breast, Mass: 150 g, Date: valid             | Food logged, calories and protein shown in success message     |                |           |           |
| 15       | Diet log validation        | Attempt to log food with non-numeric mass                               | Erroneous  | Mass: "lots"                                               | Error message: "Please enter a valid number for mass in grams" |                |           |           |
| 16       | Diet log validation        | Attempt to log food with invalid date (year > 2200)                    | Boundary   | Date: 2300-01-01                                           | Error message: "Year must be between 1900 and 2200"            |                |           |           |
| 17       | Calendar view              | View exercise logs on the calendar after logging                        | Normal     | Navigate to calendar after test 7                          | Logged exercise appears on the correct date in the calendar    |                |           |           |
| 18       | Calendar view              | Toggle to diet view and verify diet log appears                         | Normal     | Toggle to diet view after test 14                          | Logged food item appears on the correct date                   |                |           |           |
| 19       | Edit exercise log          | Edit the sets on a previously logged exercise                           | Normal     | Change sets from 3 to 4 on the bench press log from test 7 | Log updated, new value shown in calendar                       |                |           |           |
| 20       | Delete exercise log        | Delete a logged exercise entry                                          | Normal     | Delete the entry from test 7                               | Entry removed from calendar view                               |                |           |           |
| 21       | Analytics – weight graph   | Log body weight and verify it appears on the weight history graph       | Normal     | Weight: 75 kg, Date: today                                 | Data point appears on the weight history graph on analytics    |                |           |           |
| 22       | Analytics – strength graph | Filter strength graph to a specific exercise                            | Normal     | Filter to: Bench press                                     | Graph shows only bench press data points over time             |                |           |           |
| 23       | Analytics – time period    | Switch analytics chart from daily to weekly view                        | Normal     | Click "Weekly" button on any chart                         | Graph re-renders aggregated by week                            |                |           |           |
| 24       | Analytics – calorie balance| View calorie balance after logging both exercise and food               | Normal     | After tests 7 and 14                                       | Graph shows calories gained vs calories burnt and net value    |                |           |           |
| 25       | Goals                      | Create a new goal with valid details                                     | Normal     | Type: strength, Target: 100 kg, Unit: kg, Date: valid       | Goal appears in goals list with 0% progress                    |                |           |           |
| 26       | Goals – update progress    | Update the current value of a goal                                      | Normal     | Set current value to 80 kg on the goal from test 25        | Progress bar updates to 80%                                    |                |           |           |
| 27       | Goals – delete             | Delete a goal                                                           | Normal     | Delete goal from test 25                                   | Goal removed from goals list                                   |                |           |           |
| 28       | Workout presets            | Create a workout preset and add exercises to it                         | Normal     | Preset name: "Push Day", add Bench press (3×10, 60 kg)     | Preset created and exercise appears in the preset list         |                |           |           |
| 29       | Workout presets – use      | Use a preset to log a full workout                                      | Normal     | Select "Push Day" preset, confirm date, submit             | All exercises in the preset logged as separate entries         |                |           |           |
| 30       | Tips – random              | Load a random tip                                                       | Normal     | Click "Random Tip" button                                  | A tip is displayed with title, content and source              |                |           |           |
| 31       | Tips – search              | Search tips by keyword                                                  | Normal     | Keyword: "protein"                                         | Tips containing "protein" in title or content are returned     |                |           |           |
| 32       | Tips – category filter     | Filter tips to exercise category                                        | Normal     | Click "Exercise" filter button                             | Only exercise tips are displayed                               |                |           |           |
| 33       | Data persistence           | Log out and log back in; verify data is still present                   | Normal     | Log out, then log back in with same credentials            | All previously logged data still visible in calendar           |                |           |           |
| 34       | Session security           | Attempt to access dashboard URL without being logged in                 | Erroneous  | Navigate to / without a session                            | Redirected to login page                                       |                |           |           |

---

### Video Structure Guide (what to show and in what order)

Structure your recording as follows so the test numbers above align with the video:

1. **Registration and Login** (Tests 1–6): Show creating a new account, including failed attempts with mismatched passwords, weak password and duplicate username. Then log in successfully and show a failed login attempt.

2. **Exercise Logging – Gym** (Tests 7–9): Log a gym exercise (e.g. bench press, 3 sets × 10 reps, 60 kg) — show the success message with calorie estimate. Then show the erroneous tests: reps set to 0, and text entered in the weight field.

3. **Exercise Logging – Cardio and Type Filter** (Tests 10–13): Log a cardio exercise (e.g. running, 30 minutes) and show the success message. Show the duration < 1 boundary test. Then demonstrate the exercise type filter — select Gym and show only gym exercises appear in the list, then select Cardio and show only cardio exercises appear.

4. **Diet Logging** (Tests 14–16): Log a food item (e.g. chicken breast, 150 g) and show the logged macros in the success message. Then show the erroneous test with a non-numeric mass, and the boundary date test with year 2300.

5. **Calendar View** (Tests 17–20): Open the calendar and show the exercise log from step 2 appearing on the correct date. Toggle to diet view and show the food entry. Then edit the sets on the exercise log and confirm it updates. Then delete an entry and confirm it disappears.

6. **Analytics and Graphs** (Tests 21–24): Log a body weight entry, then open analytics and show the weight history graph with the new data point. Filter the strength graph to show only bench press data. Switch a chart from daily to weekly view and show it re-renders. Show the calorie balance chart with both diet and exercise data present.

7. **Goals** (Tests 25–27): Create a new goal, show it in the goals list at 0%. Update the current value and show the progress bar update. Then delete the goal.

8. **Workout Presets** (Tests 28–29): Create a new preset named "Push Day" and add an exercise. Then use that preset to log a full workout and verify the entries appear in the calendar.

9. **Tips** (Tests 30–32): Click the random tip button and show a tip loading. Search by keyword "protein" and show matching tips. Filter by "Exercise" category and show only exercise tips appearing.

10. **Data Persistence and Session Security** (Tests 33–34): Log out, then log back in and navigate to the calendar to confirm data is still present. Then try navigating to the dashboard URL without being logged in and show the redirect to the login page.

---

## SECTION 5 – Evaluation

### 5.1 How Well the Solution Meets the Requirements

*(Write 2–3 paragraphs here reviewing the solution against your User Requirements from section 1.3.4. Use the structure below — fill in the bracketed parts with honest reflection)*

Overall, the solution I developed meets the core requirements identified through my research and client interview. [Summarise here: which requirements were fully met — e.g. combining exercise and diet tracking in one place, progress graphs, user accounts, food macro database, tips system.] The program provides the kind of consolidated, visual and informative experience that both my client and the survey respondents said was absent from existing tools like freeworkoutlog.

[Add a paragraph here acknowledging what wasn't fully completed or what works differently than originally planned — e.g. custom exercise entries not implemented, any feature that was modified or cut. Be honest — this shows reflection.]

### 5.2 Evaluation Against Objectives

*(For each User Requirement you listed in section 1.3.4, copy it here and write 1–2 sentences on whether it was met and how. Follow this format:)*

**Requirement: Website combining diet tracking and exercise in one accessible location**
Met. The solution consolidates diet logging (via the FatSecret API) and exercise logging (gym and cardio) into a single web application, accessible via any browser. Users no longer need to switch between separate apps.

**Requirement: User-friendly menu where the different pages are easy to navigate**
[Write your assessment here]

**Requirement: Able to log different forms of exercises and not just gym**
Met. The exercise log supports both gym-based strength training (sets, reps, weight) and cardio exercises (type, duration), with the exercise type dynamically filtering the available exercises so only relevant options are shown.

**Requirement: Able to specify user's goal for fitness and diet tracker to target**
[Write your assessment here]

**Requirement: Sign up and log in to an account for personal data to be saved**
Met. The authentication system allows users to register with a username, email and validated password. Passwords are hashed using pbkdf2:sha256 before storage. All logged data is tied to the user's account via a userId foreign key and persists across sessions.

**Requirement: Show daily and long-term macro-nutrient progress through a database**
Met. The analytics page generates protein and calorie graphs from the user's diet logs, viewable across daily, weekly, monthly and yearly time periods. Food macros are calculated automatically from the FatSecret API at the point of logging.

**Requirement: Suggest supplements with information and research supplied**
Met. The tips database includes a supplement tip on creatine — covering dosing, benefits and a cited sports nutrition source — which is accessible on the tips page.

**Requirement: Provides advice and tips on diet and exercise with science behind it**
Met. The tips page provides a database of science-backed guidance on both exercise and diet, each with a cited source. Users can search by keyword, filter by category or load a random tip.

**Requirement: Graphs to display user statistics and progress**
Met. The analytics page provides weight history, strength progression, calorie balance and protein intake graphs, each supporting daily, weekly, monthly and yearly time views.

### 5.3 Client Feedback and Discussion

*(This section requires you to ask your mum — your client — to use the program and give you feedback. Record what she says, then write your analysis of it below. Structure it like this:)*

After completing the solution, I asked my client — my mum — to use the program and provide feedback on how well it met her needs. [Summarise what she said in a few sentences — what she liked, what she found useful, anything she found confusing or would change.]

Her feedback highlighted [pick out the most useful points — e.g. she found the graphs motivating, she found navigation easy/hard, she wanted a feature that wasn't there]. This aligns with / contrasts with the findings from my initial research in that [connect it back to your survey data and interview].

Based on her feedback, if I were to revisit the project I would [list 2–3 specific improvements — see section 5.4 below].

*(Include the full feedback — e.g. a written note or transcript — in an appendix and reference it here)*

### 5.4 Potential Improvements

If I had more time and were to revisit the project, there are several areas I would improve:

**Custom exercise entries:** One limitation I acknowledged in section 1.5 is that users cannot add a fully custom exercise to the database — they are limited to the preset list. Adding this feature, similar to freeworkoutlog's custom exercise option, would make the system far more flexible for users with niche or unique exercises in their routine.

**Macro targets and personalised daily goals:** Currently, the system logs calories and protein but does not calculate or display a daily target based on the user's goal (e.g. a caloric deficit for fat loss or a protein target based on body weight). Adding a goal-based macro target calculation — using the user's logged body weight, goal type and activity level — would make the dietary tracking far more actionable and personalised.

**Expanded food macros (carbs and fats):** The current diet log records only calories and protein. Logging carbohydrates and fats as well — which the nutritionDatabase table is already designed to support — would give users a more complete picture of their nutrition and better align with the broader macro-nutrient tracking that the user requirements described.

**Mobile responsiveness:** The current UI is functional on a desktop browser but is not fully optimised for mobile. Given that the target user would likely want to log a workout immediately after or during a session, a mobile-friendly interface would significantly improve the practical usability of the application.

---

*End of completed sections. All text above is new writing — highlight it RED in your Word document before submitting.*
