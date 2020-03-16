import React, { useState, useEffect } from 'react';
import { Header, Label, Grid, Segment, Form } from 'semantic-ui-react';
import { gql } from 'apollo-boost';
import { useQuery } from '@apollo/react-hooks';
import Questions from './Questions';
import QueueFilterForm from './QueueFilterForm';

const GET_QUESTIONS = gql`
  query GetQuestions($id: ID!) {
    queue(id: $id) {
      id
      tags
      questions {
        edges {
          node {
            id
            text
            tags
            state
            timeAsked
            timeWithdrawn
            timeRejected
            timeStarted
            timeAnswered
            orderKey
            videoChatUrl
            answeredBy {
              id
              preferredName
            }
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
    },
    pollInterval: 1000
  });

  const getQuestions = (data) => {
    if (!data) { return [] }
    return data.queue.questions.edges.map((item) => {
      return {
        id: item.node.id,
        orderKey: item.node.orderKey,
        text: item.node.text,
        tags: item.node.tags,
        state: item.node.state,
        timeAsked: item.node.timeAsked,
        askedBy: item.node.askedBy,
        timeWithdrawn: item.node.timeWithdrawn,
        timeRejected: item.node.timeRejected,
        timeStarted: item.node.timeStarted,
        timeAnswered: item.node.timeAnswered,
        answeredBy: item.node.answeredBy,
        videoChatUrl: item.node.videoChatUrl
      };
    });
  };

  /* FILTERING QUESTIONS FUNC */
  const isVisible = (question) => {
    return question.state === "ACTIVE" || question.state === "STARTED";
  };

  const filter = (questions, filters) => {
    return questions.filter(question => {
      return isSubset(question.tags, filters.tags) && isVisible(question);
    });
  };

  // Returns true if l1 is a subset of l2
  const isSubset = (l1, l2) => {
    if (l2.length === 0)  return true;
    return l1.filter(value => l2.includes(value)).length > 0;
  };

  const handleFilterChange = (input) => {
    setFilters(input);
    setFilteredQuestions(filter(questions, input));
  };

  /* STATE */
  const [queue, setQueue] = useState(props.queue);
  const [questions, setQuestions] = useState([]);
  const [filteredQuestions, setFilteredQuestions] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState({ tags: [], status: null });

  if (data && data.queue) {
    const newQuestions = getQuestions(data);
    if (JSON.stringify(newQuestions) !== JSON.stringify(questions)) {
      setQuestions(newQuestions);
      setFilteredQuestions(filter(newQuestions, filters));
    }

    if (JSON.stringify(data.queue.tags) !== JSON.stringify(tags)) {
      setTags(data.queue.tags);
    }
  }

  useEffect(() => {
    setQueue(queue);
  }, [props.queue]);

  return (
    <Segment basic>
      <Header as="h3">
        { queue.name }
        <Header.Subheader>
            { queue.description }
        </Header.Subheader>
      </Header>
      <Label
        content={ filter(questions, { tags: [] }).length + " user(s)" }
        color="blue"
        icon="user"/>
      // <Label content={queue.estimatedWaitTime + " mins"} color="blue" icon="clock"/>
      <Label as="a"
        content="Edit"
        color="grey"
        icon="cog"
        onClick={ props.editFunc }/>
      {
        tags.length > 0 && 
        <Grid.Row>
        <QueueFilterForm tags={ tags } changeFunc={ handleFilterChange }/>
        </Grid.Row>
      }
      <Grid.Row columns={1} padded="true">
          <Questions
            questions={ filteredQuestions }
            filters={ filters }
            refetch={ refetch }
            active={ queue.activeOverrideTime !== null }/>
      </Grid.Row>
    </Segment>
  );
};

export default Queue;
