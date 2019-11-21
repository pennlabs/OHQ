//fake course data for dashboard page
var fakeStudentCourses = [
  {
    code: "CIS 320",
    title: "sanjeev",
    totalQueues: "1",
    openQueues: "0",
    isArchived: false,
    year: 2019,
    semester: 0
  },
  {
    code: "CIS 380",
    title: "Operating Systems",
    totalQueues: "1",
    openQueues: "1",
    isArchived: false,
    year: 2019,
    semester: 0
  }
];

var fakeInstructorCourses = [
  {
    code: "CIS 121",
    title: "Intro to Data Structures and Algorithms",
    totalQueues: "2",
    openQueues: "1",
    isArchived: false,
    year: 2019,
    semester: 0
  },
  {
    code: "CIS 121",
    title: "Intro to Data Structures and Algorithms",
    totalQueues: "0",
    openQueues: "0",
    isArchived: true,
    year: 2018,
    semester: 1
  }
];

export { fakeStudentCourses, fakeInstructorCourses };