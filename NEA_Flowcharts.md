# NEA Flowcharts – Eothain Fernades
# Shape key used throughout:
#   (OVAL)          = Start / End (terminator)
#   [RECTANGLE]     = Process (something the program does)
#   <DIAMOND>       = Decision (a yes/no question)
#   /PARALLELOGRAM/ = Input or Output (user types something / something shown on screen)
#   ((CIRCLE))      = Connector (joins two parts of a long diagram)
#
# Arrows show the direction of flow. YES / NO labels sit on the arrow from each diamond.

==============================================================
FLOWCHART 1 – MAIN PROGRAM NAVIGATION (HIGH-LEVEL OVERVIEW)
==============================================================

(START)
    ↓
[User opens the web application in a browser]
    ↓
<Is the user logged in? (session exists?)>
    |                        |
   NO                       YES
    |                        |
    ↓                        ↓
/Show Login Page/        [Load Dashboard page]
    ↓                        ↓
/User enters            <Which page does
 username & password/    the user navigate to?>
    ↓                        |
(See Flowchart 2              |
 – Login Flow)         ┌─────┼──────┬──────────┬──────────┬──────────┐
                       ↓     ↓      ↓          ↓          ↓          ↓
                  [Exercise [Diet  [Analytics [Goals    [Tips      [Weight
                   Log]      Log]   Page]      Page]     Page]      Log]
                       ↓     ↓      ↓          ↓          ↓          ↓
                  (See    (See    (See       (See       (See       (See
                  Chart 4) Chart 5) Chart 6)  Chart 7)  Chart 8)  Chart 9)
                       |     |      |          |          |          |
                       └─────┴──────┴──────────┴──────────┴──────────┘
                                            ↓
                               [User clicks Logout]
                                            ↓
                               [Session cleared]
                                            ↓
                               /Redirected to Login Page/
                                            ↓
                                        (END)


==============================================================
FLOWCHART 2 – SIGN-UP (REGISTRATION) FLOW
==============================================================

(START)
    ↓
/User fills in Sign-Up form:
 username, email, password, confirm password/
    ↓
[Submit button pressed (POST request sent)]
    ↓
<Do password and confirm password match?>
    |                    |
   NO                   YES
    ↓                    ↓
/Flash error:        <Does password meet strength rules?
 "Passwords do        (min 8 chars, uppercase, lowercase,
 not match"/          digit, symbol – checked by valPass)>
    ↓                    |                    |
[Re-render           NO                      YES
 Sign-Up form]        ↓                       ↓
    ↑            /Flash error             <Is username OR email
    |             messages                 already in database?>
    |             (missing rules)/             |           |
    └────────────     ↓                       NO          YES
                 [Re-render                    ↓           ↓
                  Sign-Up form]           [Hash        /Flash error:
                      ↑                   password      "Username or email
                      |                   using          already exists"/
                      |                   pbkdf2:sha256]     ↓
                      |                       ↓         [Re-render
                      |                  [Save new        Sign-Up form]
                      |                   user to              ↑
                      |                   users table]         |
                      └─────────────────────────────── ────────┘
                                            ↓
                              /Flash success: "Account created"/
                                            ↓
                               [Redirect to Login page]
                                            ↓
                                        (END)


==============================================================
FLOWCHART 3 – LOGIN FLOW
==============================================================

(START)
    ↓
/User fills in Login form:
 username, password/
    ↓
[Submit button pressed (POST request sent)]
    ↓
[Search users table for entered username]
    ↓
<Is the username found in the database?>
    |                     |
   NO                    YES
    ↓                     ↓
/Flash error:       [Retrieve stored
 "Invalid username   passwordHash from
 or password"/       the database row]
    ↓                     ↓
[Re-render          <Does entered password match
 Login page]         the stored hash?
    ↑                (checked by check_password_hash)>
    |                    |                  |
    |                   NO                 YES
    |                    ↓                  ↓
    |              /Flash error:      [Store userId and
    |               "Invalid           username in session]
    └──────────────  username or            ↓
                     password"/       /Flash success:
                         ↓             "Logged in"/
                    [Re-render              ↓
                     Login page]      [Redirect to Dashboard]
                                            ↓
                                        (END)


==============================================================
FLOWCHART 4 – EXERCISE LOGGING FLOW
==============================================================

(START)
    ↓
<Is user logged in? (session check)>
    |                     |
   NO                    YES
    ↓                     ↓
[Redirect to         /Exercise Log page shown to user/
 Login page]              ↓
                     /User selects exercise type:
                      Gym or Cardio/
                          ↓
                     [JavaScript filters exercise
                      dropdown to show only the
                      matching type (gym OR cardio)]
                          ↓
                     /User selects exercise name
                      from filtered list/
                          ↓
                     /User enters date/
                          ↓
                     <Is exercise type = Gym?>
                          |              |
                         YES             NO (Cardio)
                          ↓              ↓
                     /User enters    /User enters
                      weight (kg),    duration (minutes)/
                      sets, reps/          ↓
                          ↓          <Is duration >= 1 minute?>
                     <Are weight,         |            |
                      sets and reps      NO           YES
                      valid numbers?      ↓            |
                      weight >= 0.1,  /Flash error/   |
                      sets >= 1,       ↓              |
                      reps >= 1?>  [Re-render         |
                         |  |       form]             |
                        NO YES          ↑             |
                         ↓   |         └─────────────┘
                     /Flash  |
                      error/ |
                         ↓   ↓
                    [Re-render]
                         ↑
                         |
               ┌─────────┘
               |
               ↓
          <Is date valid?
           year between
           1900 and 2200?>
               |          |
              NO          YES
               ↓           ↓
          /Flash error/ [Run binary search (binSearch)
               ↓         on sorted exercise name list
          [Re-render]    to find the exercise]
                              ↓
                         <Is exercise found
                          in the list? (index != -1)>
                              |              |
                             NO             YES
                              ↓              ↓
                         /Flash error:  [Retrieve exerciseId
                          "Exercise      from idList at
                          not found"/    matched index]
                              ↓              ↓
                         [Re-render]   [SQL query: get
                                        MET value for
                                        this exerciseId]
                                            ↓
                                       [SQL query: get user's
                                        most recent body weight
                                        from bodyWeight table]
                                        (default 70 kg if none)
                                            ↓
                                       <Is exercise type Cardio?>
                                            |              |
                                           YES             NO (Gym)
                                            ↓              ↓
                                       [time =        [Estimate time:
                                        duration        (sets × reps × 3)
                                        ÷ 60            + (sets × 60)
                                        (hours)]        ÷ 3600 (hours)]
                                            |              |
                                            └──────┬───────┘
                                                   ↓
                                       [Calculate calories:
                                        MET × weight (kg) × time (hours)
                                        rounded to 1 decimal place]
                                                   ↓
                                       [INSERT into exerciseLogs table:
                                        userId, exerciseId, date, sets,
                                        reps, weight, duration, caloriesBurned]
                                                   ↓
                                       /Flash success:
                                        "Exercise logged.
                                        Estimated calories: X cal"/
                                                   ↓
                                       [Redirect to Dashboard]
                                                   ↓
                                               (END)


==============================================================
FLOWCHART 5 – DIET LOGGING FLOW
==============================================================

(START)
    ↓
<Is user logged in? (session check)>
    |                     |
   NO                    YES
    ↓                     ↓
[Redirect to         /Diet Log page shown to user/
 Login page]              ↓
                     /User enters:
                      food name, mass (grams), date/
                          ↓
                     [Submit button pressed]
                          ↓
                     <Is mass a valid number?>
                          |               |
                         NO              YES
                          ↓               ↓
                     /Flash error:   <Is date valid?
                      "Please enter   year between
                      a valid          1900 and 2200?>
                      number"/              |          |
                          ↓               NO          YES
                     [Re-render       /Flash error/    ↓
                      Diet Log form]       ↓      [Call FatSecret API
                          ↑          [Re-render]   via calcNutrients:
                          |                         send food name
                          └──────────────────────   and mass (g)]
                                                         ↓
                                                    <Did API return
                                                     a result?>
                                                         |          |
                                                        NO         YES
                                                         ↓          ↓
                                                    /Flash error: [Extract from
                                                     "No results   API result:
                                                     found for     foodName,
                                                     that food"/   calories,
                                                         ↓         protein]
                                                    [Re-render]        ↓
                                                                  [Cache result
                                                                   in local
                                                                   nutritionDatabase
                                                                   table (per 100g)]
                                                                       ↓
                                                                  [INSERT into
                                                                   dietLogs:
                                                                   userId, foodName,
                                                                   date, mass,
                                                                   calories, protein]
                                                                       ↓
                                                                  /Flash success:
                                                                   "Logged [food]:
                                                                   Xg protein,
                                                                   X cal"/
                                                                       ↓
                                                                  [Redirect to
                                                                   Dashboard]
                                                                       ↓
                                                                   (END)


==============================================================
FLOWCHART 6 – ANALYTICS / GRAPHS PAGE FLOW
==============================================================

(START)
    ↓
<Is user logged in?>
    |              |
   NO             YES
    ↓              ↓
[Redirect to  [Render analytics.html page]
 Login]            ↓
              /Page loads — browser sends
               fetch requests for chart data/
                   ↓
              <Which chart endpoint is called?>
                   |
        ┌──────────┼──────────┬──────────┐
        ↓          ↓          ↓          ↓
  [Weight      [Strength  [Calorie   [Protein
   history      progression balance    intake
   endpoint]    endpoint]  endpoint]  endpoint]
        ↓          ↓          ↓          ↓
  [SQL: SELECT [SQL: JOIN  [SQL: GROUP [SQL: GROUP
   date, weight exerciseLogs BY date:   BY date:
   FROM body-   + exercises  SUM cals   SUM protein
   Weight WHERE table; group  burned     FROM
   userId = ?   by exercise; (exercise) dietLogs
   ORDER BY     calc weight  and gained WHERE
   date ASC]    per rep or   (diet);    userId = ?
                duration]    calc net]  ORDER date]
        ↓          ↓          ↓          ↓
        └──────────┴──────────┴──────────┘
                             ↓
                  <What time period did
                   the user select?>
                   (daily / weekly /
                    monthly / yearly)
                        |
          ┌─────────────┼──────────┬────────────┐
          ↓             ↓          ↓             ↓
      [Return       [Group by  [Group by    [Group by
       raw daily     week:      month:       year:
       data          AVG/SUM    AVG/SUM      AVG/SUM
       points]       per week]  per month]   per year]
          |             |          |             |
          └─────────────┴──────────┴─────────────┘
                             ↓
                   [Return data as JSON
                    to the browser]
                             ↓
                   /Browser renders
                    chart using the
                    JSON data/
                             ↓
                         (END)


==============================================================
FLOWCHART 7 – GOALS FLOW
==============================================================

(START)
    ↓
<Is user logged in?>
    |              |
   NO             YES
    ↓              ↓
[Redirect]   [Load all goals for this user
              from goals table (ORDER BY
              createdAt DESC) as Goal objects]
                   ↓
             /Show goals page with
              list of current goals
              and Create Goal form/
                   ↓
             <What does the user do?>
                   |
        ┌──────────┼────────────┬─────────────┐
        ↓          ↓            ↓              ↓
  [Create       [Update      [Edit          [Delete
   new goal]     progress     goal           goal]
        ↓         (current     details]          ↓
  /User fills    value)]           ↓        [SQL: DELETE
   in type,           ↓       /User edits   FROM goals
   target,       /User enters  description, WHERE id = ?
   date, unit,   new current   target,      AND userId=?]
   description/   value/        date, unit/      ↓
        ↓              ↓             ↓       [Redirect to
  [Create new    [Goal.saveToDB: [Goal.saveToDB: Goals page]
   Goal object    UPDATE goals   UPDATE goals
   (goalID=None)] SET currentValue SET targetValue
        ↓         WHERE id=?]    etc WHERE id=?]
  [Goal.saveToDB:       ↓              ↓
   INSERT INTO     [Redirect]     [Redirect]
   goals table]
        ↓
  [Redirect to
   Goals page]
        ↓
  /calcProgress():
   (currentValue /
    targetValue)
    × 100
   shown as % bar/
        ↓
    (END)


==============================================================
FLOWCHART 8 – TIPS PAGE FLOW
==============================================================

(START)
    ↓
<Is user logged in?>
    |              |
   NO             YES
    ↓              ↓
[Redirect]   /Tips page shown:
              Random Tip button,
              Exercise / Diet
              filter buttons,
              Search bar/
                   ↓
             <What does the user do?>
                   |
        ┌──────────┼──────────┐
        ↓          ↓          ↓
  [Random Tip]  [Filter by  [Search by
        ↓        category]   keyword]
  [SQL: SELECT       ↓            ↓
   all tips;    [SQL: SELECT  [SQL: SELECT
   Python:       WHERE        WHERE title
   random.       category     LIKE %keyword%
   choice()]     = 'exercise'  OR content
        ↓        OR 'diet']    LIKE %keyword%]
        |             ↓            ↓
        |        [Enqueue results into Queue
        |         data structure (FIFO);
        |         dequeue in order to
        |         build tipsList]
        |             ↓            ↓
        └─────────────┴────────────┘
                       ↓
             /Return tip(s) as JSON;
              display on page/
                       ↓
                   (END)


==============================================================
HOW TO DRAW THESE IN DRAW.IO – QUICK GUIDE
==============================================================

Shape         | draw.io shape to use          | When to use
--------------|-------------------------------|----------------------------------
(OVAL)        | Terminator (rounded ends)     | START and END only
[RECTANGLE]   | Process (plain rectangle)     | Any action the program takes
<DIAMOND>     | Decision (rotated square)     | Any Yes/No condition or check
/PARALLELOGRAM| Input/Output (slanted sides)  | User types something OR
              |                               | something displayed to user
((CIRCLE))    | Connector (small circle)      | To continue diagram on next page

ARROW RULES:
- One arrow going IN to each shape (except START which has none)
- One arrow going OUT of most shapes
- TWO arrows going out of a DIAMOND, labelled YES and NO
- Arrows from diamonds go: NO → usually loops back to the form
                           YES → continues down the main flow

TIP: In draw.io, search the shape panel for "flowchart" to get all these shapes.
     Use Edit > XML if you want to paste shapes in bulk.
