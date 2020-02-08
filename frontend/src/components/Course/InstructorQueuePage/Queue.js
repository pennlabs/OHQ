import React, { useState } from 'react';
import { Header, Label, Grid, Segment } from 'semantic-ui-react';
import { gql } from 'apollo-boost';
import { useQuery } from '@apollo/react-hooks';
import Questions from './Questions';

const GET_QUESTIONS = gql`
  query GetQuestions($id: ID!) {
    queue(id: $id) {
      id
      questions {
        edges {
          node {
            id
            text
            tags
            timeAsked
            askedBy {
              id
              preferredName
            }
          }
        }
      }
    }
  }
`;

const Queue = (props) => {
  const { loading, error, data, refetch } = useQuery(GET_QUESTIONS, {
    variables: {
      id: props.queue.id
    }
  });

  const getQuestions = (data) => {
    var newQuestions = [];
    data && data.queue.questions.edges.map((node) => {
      newQuestions.push({
        id: node.id,
        text: node.text,
        tags: node.tags,
        timeAsked: node.timeAsked,
        askedBy: node.askedBy
      })
    });
    return newQuestions;
  }

  const [queue, setQueue] = useState(props.queue);
  const [questions, setQuestions] = useState(getQuestions(data));

  return (
    <Segment basic>
      <Header as="h3">
        { queue.name }
        <Header.Subheader>
            { queue.description }
        </Header.Subheader>
      </Header>
      <Label
        content={ questions && questions.length + " users" }
        color="blue"
        icon="user"
      />
      <Label content="30 mins" color="blue" icon="clock"/>
      <Label as="a"
        content="Edit"
        color="grey"
        icon="cog"
        onClick={ props.editFunc }
      />
      <Grid.Row columns={1} padded="true">
          <Questions questions={ questions }/>
      </Grid.Row>
    </Segment>
  );
}

export default Queue;