import React from 'react';
import { Segment, Menu, Header, Grid, Modal, Form } from 'semantic-ui-react';
import CourseCard from './CourseCard';
import ArchivedCourseCard from './ArchivedCourseCard';
import AddCard from './AddCard';
import ModalAddStudentCourse from './ModalAddStudentCourse';
import { fakeStudentCourses, fakeInstructorCourses } from './coursedata.js';

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showArchived: false,
      studentCourses: [],
      instructorCourses: [],
      newStudentCourse: {
        code: "",
        title: "",
      },
      studentModalOpen: false
    };

    this.handleArchivedChange = this.handleArchivedChange.bind(this);
    this.handleStudentCourseSubmit = this.handleStudentCourseSubmit.bind(this);
    this.handleStudentCourseChange = this.handleStudentCourseChange.bind(this);
    this.openStudentModal = this.openStudentModal.bind(this);
  }

  handleArchivedChange() {
    this.setState({ showArchived: !this.state.showArchived });
  }

  openStudentModal() {
    this.setState({ studentModalOpen: true });
  }

  handleStudentCourseSubmit() {
    var newStudentCourses = this.state.studentCourses;
    var newCourse = {
      code: this.state.newStudentCourse.code,
      title: this.state.newStudentCourse.title,
      totalQueues: "1",
      openQueues: "0",
      isArchived: false,
      year: 2019,
      semester: 0
    };
    newStudentCourses.push(newCourse)
    this.setState({ studentCourses: newStudentCourses, studentModalOpen: false });
  }

  handleStudentCourseChange(e, { name, value }) {
    var course = this.state.newStudentCourse;
    course[name] = value;
    this.setState({ newStudentCourse: course });
  }

  componentDidMount() {
    this.setState({
      studentCourses: fakeStudentCourses,
      instructorCourses: fakeInstructorCourses
    });
  }

  render() {
    return (
      <Grid columns={2} divided="horizontally">
        <Grid.Column width={3}>
          <Segment basic>
          <Menu vertical secondary fluid>
            <Menu.Item
              name="Dashboard"
              onClick={function(){}}
            />
          </Menu>
          </Segment>
        </Grid.Column>
        <Grid.Column width={13}>
          <Grid padded>
            <Segment basic padded>
              <Header as="h2">
                <Header.Content>
                  Student Courses
                </Header.Content>
              </Header>
            </Segment>
            {/* add student course cards */}
            <Grid.Row columns={4} padded>
                {
                  this.state.studentCourses.map(course => (

                    !course.isArchived &&
                    <Grid.Column>
                      <CourseCard
                        code={course.code}
                        title={course.title}
                        totalQueues={course.totalQueues}
                        openQueues={course.openQueues}
                        isArchived={course.isArchived}
                      />
                    </Grid.Column>
                  ))
                }
                <Grid.Column>
                  <AddCard clickFunc={this.openStudentModal}/>
                  <ModalAddStudentCourse
                    changeFunc={this.handleStudentCourseChange}
                    submitFunc={this.handleStudentCourseSubmit}
                    open={this.state.studentModalOpen}
                  />
                </Grid.Column>
            </Grid.Row>
            <Segment basic padded>
              <Header as="h2">
                <Header.Content>
                  Instructor Courses
                </Header.Content>
              </Header>
            </Segment>
            {/* add instructor course cards */}
            <Grid.Row columns={4} padded>
                {
                  this.state.instructorCourses.map(course => (

                    !course.isArchived &&
                    <Grid.Column>
                      <CourseCard
                        code={course.code}
                        title={course.title}
                        totalQueues={course.totalQueues}
                        openQueues={course.openQueues}
                        isArchived={course.isArchived}
                      />
                    </Grid.Column>
                  ))
                }
            </Grid.Row>
            <a style={{"text-decoration":"underline"}} onClick={this.handleArchivedChange}>
              { this.state.showArchived ? "Hide Archived Courses" : "See Archived Courses"}
            </a>
            {/* add archived instructor courses if "see archived" is toggled */}
            <Grid.Row columns={4} padded>
                {
                  this.state.instructorCourses.map(course => (

                    this.state.showArchived && course.isArchived &&
                    <Grid.Column>
                      <ArchivedCourseCard
                        code={course.code}
                        title={course.title}
                        isArchived={course.isArchived}
                        year={course.year}
                      />
                    </Grid.Column>
                  ))
                }
            </Grid.Row>
          </Grid>
        </Grid.Column>
      </Grid>
    );
  }
}