import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.util.zip.*;

import cc.mallet.fst.*;
import cc.mallet.pipe.*;
import cc.mallet.pipe.iterator.*;
import cc.mallet.pipe.tsf.*;
import cc.mallet.types.*;
import cc.mallet.util.*;


public class CRFTest{
	public CRFTest(String trainingFilename, String testingFilename) throws IOException {
			
			ArrayList<Pipe> pipes = new ArrayList<Pipe>();
	
			pipes.add(new SimpleTaggerSentence2TokenSequence());
			pipes.add(new TokenTextCharSuffix("delete=", 1));
			pipes.add(new TokenTextCharSuffix("sausage_length=", 4));
			pipes.add(new TokenTextCharSuffix("slot_best_length=", 1));
			pipes.add(new TokenTextCharSuffix("slot_entropy=", 3));
			pipes.add(new TokenTextCharSuffix("slot_highest=", 4));
			pipes.add(new TokenTextCharSuffix("slot_mean=", 4));
			pipes.add(new TokenTextCharSuffix("slot_position=", 1));
			pipes.add(new TokenTextCharSuffix("slot_stdev=", 4));
			pipes.add(new TokenSequence2FeatureVectorSequence());
	
			Pipe pipe = new SerialPipes(pipes);
	
			InstanceList trainingInstances = new InstanceList(pipe);
			InstanceList testingInstances = new InstanceList(pipe);
	
			trainingInstances.addThruPipe(new LineGroupIterator(new BufferedReader(new InputStreamReader(new FileInputStream(trainingFilename))), Pattern.compile("^\\s*$"), true));
			testingInstances.addThruPipe(new LineGroupIterator(new BufferedReader(new InputStreamReader(new FileInputStream(testingFilename))), Pattern.compile("^\\s*$"), true));
			
			CRF crf = new CRF(pipe, null);
			crf.addStatesForThreeQuarterLabelsConnectedAsIn(trainingInstances);
			crf.addStartState();
	
			CRFTrainerByLabelLikelihood trainer = 
				new CRFTrainerByLabelLikelihood(crf);
			//trainer.setGaussianPriorVariance(10.0);
	
			//CRFTrainerByStochasticGradient trainer = 
			//new CRFTrainerByStochasticGradient(crf, 1.0);
	
			//CRFTrainerByL1LabelLikelihood trainer = 
			//	new CRFTrainerByL1LabelLikelihood(crf, 0.75);
			

			PerClassAccuracyEvaluator trainingEvaluator = new PerClassAccuracyEvaluator(trainingInstances, "training");
			trainer.addEvaluator(trainingEvaluator);
			PerClassAccuracyEvaluator testingEvaluator = new PerClassAccuracyEvaluator(testingInstances, "testing");
			trainer.addEvaluator(testingEvaluator);
			trainer.train(trainingInstances);

			
		}

		public static void main (String[] args) throws Exception {
			CRFTest trainer = new CRFTest(args[0], args[1]);
	
		}
}

