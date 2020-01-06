import React from 'react';
import { Segment, Menu, Header, Grid, Dropdown, Checkbox, Form, Button, Input } from 'semantic-ui-react';
import Sidebar from '../Sidebar';

import { withAuthorization } from '../Session';
import { compose } from 'recompose';

const semesterOptions = [
  {
    key: 'Fall',
    text: 'Fall',
    value: 'Fall',
  },
  {
    key: 'Spring',
    text: 'Spring',
    value: 'Spring',
  },
  {
    key: 'Summer',
    text: 'Summer',
    value: 'Summer',
  },
]

const departmentOptions = [
  {
    key: 'CIS',
    text: 'CIS',
    value: 'CIS',
  },
  {
    key: 'MATH',
    text: 'MATH',
    value: 'MATH',
  },
  {
    key: 'PSYC',
    text: 'PSYC',
    value: 'PSYC',
  },
]

class CourseSettings extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
          course: {
            name: 'CIS 121',
            description: 'Introduction to Data Structures and Algorithms'
          },
          allTags: [],
          questionToDelete: {},
          deleteModal: {
            open: false,
            reason: "",
            textDisabled: true,
            text: ""
          },
          tagModal: {
            open: false
          },
          tagToAdd: "",
          editQueueModal: {
            open: false,
            queue: {}
          }
        };

      }

      render() {
        return (
          <Grid columns={2} divided="horizontally" style={{"width":"100%"}}>
            <Sidebar active={'course_settings'}/>
            <Grid.Column width={13}>
              <Grid columns={2} padded>
                <Grid.Row>
                  {/* COURSE HEADER */}
                  <Segment basic>
                    <Header as="h1">
                      {this.state.course.name}
                      <Header.Subheader>
                        {this.state.course.description}
                      </Header.Subheader>
                    </Header>
                  </Segment>
                </Grid.Row>
                <Grid.Row>
                  <Segment basic>
                    <Form>
                      <Form.Field>
                        <label>Course Department</label>
                        <Dropdown
                          placeholder='Select Department'
                          fluid
                          selection
                          options={departmentOptions}
                        />
                      </Form.Field>
                      <Form.Field>
                        <label>Course Number</label>
                        <input placeholder='Course Number' />
                      </Form.Field>
                      <Form.Field>
                        <label>Course Description</label>
                        <input placeholder='Course Description' />
                      </Form.Field>
                      <Form.Field>
                        <label>Year</label>
                        <input placeholder='Year' />
                      </Form.Field>
                      <Form.Field>
                        <label>Semester</label>
                        <Dropdown
                          placeholder='Select Semester'
                          fluid
                          selection
                          options={semesterOptions}
                        />
                      </Form.Field>
                      <Form.Field>
                        <Checkbox toggle label='TODO: something about deactivating course here' />
                      </Form.Field>
                      <Button type='submit'>Submit</Button>
                    </Form>
                  </Segment>
                </Grid.Row>
              </Grid>
            </Grid.Column>
          </Grid>
        );
      }

}

const condition = authUser => !!authUser;

export default compose(
  withAuthorization(condition),
)(CourseSettings);
