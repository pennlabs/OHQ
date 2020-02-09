import React, { useState, useEffect } from 'react';
import { Segment, Form, Header, Button } from 'semantic-ui-react';
import { gql } from 'apollo-boost';
import { useMutation } from '@apollo/react-hooks'; 

const CREATE_QUESTION = gql`
  mutation CreateQuestion($input: CreateQuestionInput!) {
    createQuestion(input: $input) {
      question {
        id
      }
    }
  }
`;

const QuestionForm = (props) => {
  const [createQuestion, { loading, data }] = useMutation(CREATE_QUESTION);
  const [queue, setQueue] = useState(props.queue);
  const [success, setSuccess] = useState(false);
  const [input, setInput] = useState({
    queueId: props.queue.id,
    text: "",
    tags: []
  });

  const handleInputChange = (e, { name, value }) => {
    input[name] = value;
    setInput(input);
  }

  const getDropdownOptions = (tags) => {
    var options = [];
    tags.map((tag) => {
      options.push({
        key: tag,
        value: tag,
        text: tag
      });
    });
    return options
  }

  const onSubmit = () => {
    createQuestion({
      variables: {
        input: input
      }
    }).then(() => {
      props.refetch();
      setSuccess(true);
    })
  }

  console.log(queue.id);

  useEffect(() => {
    setQueue(props.queue);
  }, [props.queue]);

  return (
    queue && <div>
      <Segment style={{"marginTop":"20px"}} attached="top" color="blue">
        <Header content="Add a Question"/>
      </Segment>
      <Segment attached secondary>
        <Form>
          <Form.Field>
            <label>Question</label>
            <Form.Input
              name="text"
              disabled={loading}
              onChange={ handleInputChange }/>
          </Form.Field>
          <Form.Field>
            <label>Tags</label>
            <Form.Dropdown multiple selection
            name="tags"
            disabled={loading}
            onChange={ handleInputChange }
            options={ getDropdownOptions(queue.tags) } />
          </Form.Field>
        </Form>
      </Segment>
      <Segment attached="bottom">
        <Button compact
          content="Submit"
          color="blue"
          disabled={ loading } 
          onClick={ onSubmit() }/>
          {
            !loading && success && <span>Added!</span>
          }
          {
            loading && <span>Adding...</span>
          }
      </Segment>
    </div>
  );
}

export default QuestionForm;